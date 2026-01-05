using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using NextGenSoftware.OASIS.API.Core.Enums;
using NextGenSoftware.OASIS.API.Core.Interfaces;
using NextGenSoftware.OASIS.API.Core.Interfaces.Agent;
using NextGenSoftware.OASIS.API.Core.Objects.NFT.Request;
using NextGenSoftware.OASIS.Common;
using NextGenSoftware.OASIS.API.DNA;
using NextGenSoftware.Logging;
using NextGenSoftware.OASIS.API.ONODE.Core.Managers;

namespace NextGenSoftware.OASIS.API.Core.Managers
{
    /// <summary>
    /// A2A Protocol integration with NFTManager
    /// Handles agent reputation NFTs, service completion certificates, and achievement badges
    /// </summary>
    public partial class A2AManager
    {
        /// <summary>
        /// Create a reputation NFT for an agent
        /// </summary>
        /// <param name="agentId">The agent ID</param>
        /// <param name="reputationScore">The reputation score</param>
        /// <param name="description">Optional description</param>
        /// <param name="imageUrl">Optional image URL for the NFT</param>
        /// <returns>NFT transaction result</returns>
        public async Task<OASISResult<object>> CreateAgentReputationNFTAsync(
            Guid agentId,
            decimal reputationScore,
            string description = null,
            string imageUrl = null)
        {
            var result = new OASISResult<object>();
            try
            {
                // Validate agent exists
                var avatarResult = await AvatarManager.Instance.LoadAvatarAsync(agentId, false, true);
                if (avatarResult.IsError || avatarResult.Result == null)
                {
                    OASISErrorHandling.HandleError(ref result, $"Agent {agentId} not found");
                    return result;
                }

                if (avatarResult.Result.AvatarType.Value != AvatarType.Agent)
                {
                    OASISErrorHandling.HandleError(ref result, $"Avatar {agentId} is not an Agent type");
                    return result;
                }

                // Get agent capabilities for metadata
                var agentCardResult = await AgentManager.Instance.GetAgentCardAsync(agentId);
                var agentCard = agentCardResult.Result;

                // Create NFT metadata
                var metadata = new Dictionary<string, object>
                {
                    ["agent_id"] = agentId.ToString(),
                    ["reputation_score"] = reputationScore,
                    ["nft_type"] = "agent_reputation",
                    ["timestamp"] = DateTime.UtcNow.ToString("O"),
                    ["agent_name"] = agentCard?.Name ?? "Unknown Agent"
                };

                if (agentCard?.Capabilities != null)
                {
                    metadata["services"] = agentCard.Capabilities.Services ?? new List<string>();
                    metadata["skills"] = agentCard.Capabilities.Skills ?? new List<string>();
                }

                // Create NFT request
                var nftRequest = new MintWeb4NFTRequest
                {
                    MintedByAvatarId = agentId,
                    Title = $"Agent Reputation - {agentCard?.Name ?? agentId.ToString()}",
                    Description = description ?? $"Reputation NFT for agent with score: {reputationScore}",
                    ImageUrl = imageUrl ?? "https://oasisplatform.io/images/agent-reputation-nft.png", // Default image
                    MetaData = metadata,
                    NumberToMint = 1,
                    StoreNFTMetaDataOnChain = false, // Store metadata off-chain for efficiency
                    OnChainProvider = new EnumValue<ProviderType>(ProviderType.SolanaOASIS), // Default to Solana
                    OffChainProvider = new EnumValue<ProviderType>(ProviderType.IPFSOASIS), // Store metadata on IPFS
                    NFTStandardType = new EnumValue<NFTStandardType>(NFTStandardType.ERC721),
                    WaitTillNFTMinted = true,
                    WaitForNFTToMintInSeconds = 60,
                    SendToAvatarAfterMintingId = agentId // Send to the agent
                };

                // Mint NFT using NFTManager
                var nftManager = new NFTManager(agentId, ProviderManager.Instance.OASISDNA);
                var nftResult = await nftManager.MintNftAsync(nftRequest);

                if (nftResult.IsError)
                {
                    OASISErrorHandling.HandleError(ref result, $"Failed to mint reputation NFT: {nftResult.Message}");
                    return result;
                }

                result.Result = nftResult.Result;
                result.Message = "Reputation NFT created successfully";
                LoggingManager.Log($"Reputation NFT created for agent {agentId} with score {reputationScore}", LogType.Info);
            }
            catch (Exception ex)
            {
                OASISErrorHandling.HandleError(ref result, $"Error creating reputation NFT: {ex.Message}", ex);
            }
            return result;
        }

        /// <summary>
        /// Create a service completion certificate NFT for an agent
        /// </summary>
        /// <param name="agentId">The agent ID</param>
        /// <param name="serviceName">The service that was completed</param>
        /// <param name="taskId">Optional task/message ID</param>
        /// <param name="description">Optional description</param>
        /// <param name="imageUrl">Optional image URL for the certificate</param>
        /// <returns>NFT transaction result</returns>
        public async Task<OASISResult<object>> CreateServiceCompletionCertificateAsync(
            Guid agentId,
            string serviceName,
            Guid? taskId = null,
            string description = null,
            string imageUrl = null)
        {
            var result = new OASISResult<object>();
            try
            {
                // Validate agent exists
                var avatarResult = await AvatarManager.Instance.LoadAvatarAsync(agentId, false, true);
                if (avatarResult.IsError || avatarResult.Result == null)
                {
                    OASISErrorHandling.HandleError(ref result, $"Agent {agentId} not found");
                    return result;
                }

                if (avatarResult.Result.AvatarType.Value != AvatarType.Agent)
                {
                    OASISErrorHandling.HandleError(ref result, $"Avatar {agentId} is not an Agent type");
                    return result;
                }

                // Create certificate metadata
                var metadata = new Dictionary<string, object>
                {
                    ["agent_id"] = agentId.ToString(),
                    ["service_name"] = serviceName,
                    ["nft_type"] = "service_completion_certificate",
                    ["timestamp"] = DateTime.UtcNow.ToString("O"),
                    ["certificate_type"] = "service_completion"
                };

                if (taskId.HasValue)
                {
                    metadata["task_id"] = taskId.Value.ToString();
                }

                // Create NFT request
                var nftRequest = new MintWeb4NFTRequest
                {
                    MintedByAvatarId = agentId,
                    Title = $"Service Completion Certificate - {serviceName}",
                    Description = description ?? $"Certificate for completing service: {serviceName}",
                    ImageUrl = imageUrl ?? "https://oasisplatform.io/images/service-certificate-nft.png",
                    MetaData = metadata,
                    NumberToMint = 1,
                    StoreNFTMetaDataOnChain = false,
                    OnChainProvider = new EnumValue<ProviderType>(ProviderType.SolanaOASIS),
                    OffChainProvider = new EnumValue<ProviderType>(ProviderType.IPFSOASIS),
                    NFTStandardType = new EnumValue<NFTStandardType>(NFTStandardType.ERC721),
                    WaitTillNFTMinted = true,
                    WaitForNFTToMintInSeconds = 60,
                    SendToAvatarAfterMintingId = agentId
                };

                // Mint NFT
                var nftManager = new NFTManager(agentId, ProviderManager.Instance.OASISDNA);
                var nftResult = await nftManager.MintNftAsync(nftRequest);

                if (nftResult.IsError)
                {
                    OASISErrorHandling.HandleError(ref result, $"Failed to mint certificate NFT: {nftResult.Message}");
                    return result;
                }

                result.Result = nftResult.Result;
                result.Message = "Service completion certificate created successfully";
                LoggingManager.Log($"Service completion certificate created for agent {agentId} for service {serviceName}", LogType.Info);
            }
            catch (Exception ex)
            {
                OASISErrorHandling.HandleError(ref result, $"Error creating service certificate: {ex.Message}", ex);
            }
            return result;
        }

        /// <summary>
        /// Create an achievement badge NFT for an agent
        /// </summary>
        /// <param name="agentId">The agent ID</param>
        /// <param name="achievementName">The achievement name</param>
        /// <param name="achievementDescription">The achievement description</param>
        /// <param name="imageUrl">Optional image URL for the badge</param>
        /// <returns>NFT transaction result</returns>
        public async Task<OASISResult<object>> CreateAchievementBadgeAsync(
            Guid agentId,
            string achievementName,
            string achievementDescription,
            string imageUrl = null)
        {
            var result = new OASISResult<object>();
            try
            {
                // Validate agent exists
                var avatarResult = await AvatarManager.Instance.LoadAvatarAsync(agentId, false, true);
                if (avatarResult.IsError || avatarResult.Result == null)
                {
                    OASISErrorHandling.HandleError(ref result, $"Agent {agentId} not found");
                    return result;
                }

                if (avatarResult.Result.AvatarType.Value != AvatarType.Agent)
                {
                    OASISErrorHandling.HandleError(ref result, $"Avatar {agentId} is not an Agent type");
                    return result;
                }

                // Create badge metadata
                var metadata = new Dictionary<string, object>
                {
                    ["agent_id"] = agentId.ToString(),
                    ["achievement_name"] = achievementName,
                    ["achievement_description"] = achievementDescription,
                    ["nft_type"] = "achievement_badge",
                    ["timestamp"] = DateTime.UtcNow.ToString("O")
                };

                // Create NFT request
                var nftRequest = new MintWeb4NFTRequest
                {
                    MintedByAvatarId = agentId,
                    Title = $"Achievement Badge - {achievementName}",
                    Description = achievementDescription,
                    ImageUrl = imageUrl ?? "https://oasisplatform.io/images/achievement-badge-nft.png",
                    MetaData = metadata,
                    NumberToMint = 1,
                    StoreNFTMetaDataOnChain = false,
                    OnChainProvider = new EnumValue<ProviderType>(ProviderType.SolanaOASIS),
                    OffChainProvider = new EnumValue<ProviderType>(ProviderType.IPFSOASIS),
                    NFTStandardType = new EnumValue<NFTStandardType>(NFTStandardType.ERC721),
                    WaitTillNFTMinted = true,
                    WaitForNFTToMintInSeconds = 60,
                    SendToAvatarAfterMintingId = agentId
                };

                // Mint NFT
                var nftManager = new NFTManager(agentId, ProviderManager.Instance.OASISDNA);
                var nftResult = await nftManager.MintNftAsync(nftRequest);

                if (nftResult.IsError)
                {
                    OASISErrorHandling.HandleError(ref result, $"Failed to mint achievement badge: {nftResult.Message}");
                    return result;
                }

                result.Result = nftResult.Result;
                result.Message = "Achievement badge created successfully";
                LoggingManager.Log($"Achievement badge created for agent {agentId}: {achievementName}", LogType.Info);
            }
            catch (Exception ex)
            {
                OASISErrorHandling.HandleError(ref result, $"Error creating achievement badge: {ex.Message}", ex);
            }
            return result;
        }
    }
}

