# OpenSERV Bridge Service Design Document

**Date:** January 5, 2026  
**Status:** ✅ **Design Complete**  
**Brief:** Brief 2 - OpenSERV API Research & Bridge Design

---

## Executive Summary

This document provides the complete design for the OpenSERV Bridge Service, which enables C# integration with OpenSERV platform. The design includes HTTP client wrapper, request/response models, error handling, retry logic, and integration patterns.

---

## 1. Architecture Overview

### 1.1 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    OASIS A2A Protocol                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐         ┌──────────────────┐        │
│  │  A2AController   │────────►│ OpenServBridge  │        │
│  │                  │         │    Service       │        │
│  └──────────────────┘         └──────────────────┘        │
│                                      │                      │
│                                      │ HTTP/REST            │
│                                      ▼                      │
│  ┌──────────────────────────────────────────────┐            │
│  │         OpenSERV Platform API              │            │
│  │      (https://api.openserv.ai)             │            │
│  └──────────────────────────────────────────────┘            │
│                                      │                      │
│                                      │ Webhooks             │
│                                      ▼                      │
│  ┌──────────────────┐         ┌──────────────────┐        │
│  │  Webhook        │────────►│  A2A Protocol    │        │
│  │  Controller     │         │  Message Queue   │        │
│  └──────────────────┘         └──────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Component Responsibilities

**OpenServBridgeService:**
- HTTP client wrapper for OpenSERV API
- Request/response serialization
- Authentication handling
- Error handling and retry logic
- Rate limit management

**A2AManager-OpenSERV:**
- Integration with A2A Protocol
- Agent registration mapping
- Workflow execution routing
- Message transformation

**Webhook Controller:**
- Receives webhooks from OpenSERV
- Signature verification
- Routes to A2A Protocol

---

## 2. OpenServBridgeService Design

### 2.1 Class Structure

```csharp
namespace NextGenSoftware.OASIS.API.ONODE.WebAPI.Services
{
    /// <summary>
    /// Bridge service for integrating with OpenSERV platform
    /// Handles HTTP communication, authentication, and error handling
    /// </summary>
    public class OpenServBridgeService : IDisposable
    {
        private readonly HttpClient _httpClient;
        private readonly IConfiguration _configuration;
        private readonly ILogger<OpenServBridgeService> _logger;
        private readonly string _apiKey;
        private readonly string _baseUrl;
        private readonly int _maxRetries;
        private readonly TimeSpan _timeout;
        
        // Constructor
        // Methods for agent registration
        // Methods for workflow execution
        // Methods for webhook handling
        // Error handling and retry logic
    }
}
```

### 2.2 Constructor Design

```csharp
public OpenServBridgeService(
    HttpClient httpClient,
    IConfiguration configuration,
    ILogger<OpenServBridgeService> logger)
{
    _httpClient = httpClient ?? throw new ArgumentNullException(nameof(httpClient));
    _configuration = configuration ?? throw new ArgumentNullException(nameof(configuration));
    _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    
    // Configuration
    _apiKey = _configuration["OpenServ:ApiKey"] 
        ?? throw new InvalidOperationException("OpenServ:ApiKey not configured");
    _baseUrl = _configuration["OpenServ:BaseUrl"] ?? "https://api.openserv.ai";
    _maxRetries = int.Parse(_configuration["OpenServ:MaxRetries"] ?? "3");
    _timeout = TimeSpan.FromSeconds(
        int.Parse(_configuration["OpenServ:TimeoutSeconds"] ?? "30"));
    
    // Configure HTTP client
    _httpClient.BaseAddress = new Uri(_baseUrl);
    _httpClient.Timeout = _timeout;
    _httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {_apiKey}");
    _httpClient.DefaultRequestHeaders.Add("Accept", "application/json");
    _httpClient.DefaultRequestHeaders.Add("User-Agent", "OASIS-A2A-OpenServ-Bridge/1.0");
}
```

### 2.3 Agent Registration Methods

```csharp
/// <summary>
/// Register an OpenSERV agent
/// </summary>
public async Task<OASISResult<OpenServAgentResponse>> RegisterAgentAsync(
    OpenServAgentRequest request)
{
    var result = new OASISResult<OpenServAgentResponse>();
    
    try
    {
        // Validate request
        if (request == null)
        {
            OASISErrorHandling.HandleError(ref result, "Request cannot be null");
            return result;
        }
        
        // Serialize request
        var jsonContent = JsonSerializer.Serialize(request);
        var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");
        
        // Execute with retry logic
        var response = await ExecuteWithRetryAsync(
            async () => await _httpClient.PostAsync("/api/v1/agents/register", content));
        
        // Handle response
        if (response.IsSuccessStatusCode)
        {
            var responseContent = await response.Content.ReadAsStringAsync();
            result.Result = JsonSerializer.Deserialize<OpenServAgentResponse>(responseContent);
            result.Message = "Agent registered successfully";
        }
        else
        {
            await HandleErrorResponseAsync(response, ref result);
        }
    }
    catch (Exception ex)
    {
        OASISErrorHandling.HandleError(ref result, 
            $"Error registering OpenSERV agent: {ex.Message}", ex);
    }
    
    return result;
}

/// <summary>
/// Get agent status
/// </summary>
public async Task<OASISResult<OpenServAgentStatus>> GetAgentStatusAsync(string agentId)
{
    var result = new OASISResult<OpenServAgentStatus>();
    
    try
    {
        if (string.IsNullOrEmpty(agentId))
        {
            OASISErrorHandling.HandleError(ref result, "Agent ID cannot be empty");
            return result;
        }
        
        var response = await ExecuteWithRetryAsync(
            async () => await _httpClient.GetAsync($"/api/v1/agents/{agentId}/status"));
        
        if (response.IsSuccessStatusCode)
        {
            var responseContent = await response.Content.ReadAsStringAsync();
            result.Result = JsonSerializer.Deserialize<OpenServAgentStatus>(responseContent);
        }
        else
        {
            await HandleErrorResponseAsync(response, ref result);
        }
    }
    catch (Exception ex)
    {
        OASISErrorHandling.HandleError(ref result, 
            $"Error getting agent status: {ex.Message}", ex);
    }
    
    return result;
}
```

### 2.4 Workflow Execution Methods

```csharp
/// <summary>
/// Execute a workflow via OpenSERV
/// </summary>
public async Task<OASISResult<OpenServWorkflowResponse>> ExecuteWorkflowAsync(
    OpenServWorkflowRequest request)
{
    var result = new OASISResult<OpenServWorkflowResponse>();
    
    try
    {
        if (request == null)
        {
            OASISErrorHandling.HandleError(ref result, "Request cannot be null");
            return result;
        }
        
        var jsonContent = JsonSerializer.Serialize(request);
        var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");
        
        var response = await ExecuteWithRetryAsync(
            async () => await _httpClient.PostAsync("/api/v1/workflows/execute", content));
        
        if (response.IsSuccessStatusCode)
        {
            var responseContent = await response.Content.ReadAsStringAsync();
            result.Result = JsonSerializer.Deserialize<OpenServWorkflowResponse>(responseContent);
            result.Message = "Workflow executed successfully";
        }
        else
        {
            await HandleErrorResponseAsync(response, ref result);
        }
    }
    catch (Exception ex)
    {
        OASISErrorHandling.HandleError(ref result, 
            $"Error executing workflow: {ex.Message}", ex);
    }
    
    return result;
}

/// <summary>
/// Get workflow status (for async workflows)
/// </summary>
public async Task<OASISResult<OpenServWorkflowResponse>> GetWorkflowStatusAsync(
    string workflowExecutionId)
{
    var result = new OASISResult<OpenServWorkflowResponse>();
    
    try
    {
        if (string.IsNullOrEmpty(workflowExecutionId))
        {
            OASISErrorHandling.HandleError(ref result, "Workflow execution ID cannot be empty");
            return result;
        }
        
        var response = await ExecuteWithRetryAsync(
            async () => await _httpClient.GetAsync(
                $"/api/v1/workflows/{workflowExecutionId}/status"));
        
        if (response.IsSuccessStatusCode)
        {
            var responseContent = await response.Content.ReadAsStringAsync();
            result.Result = JsonSerializer.Deserialize<OpenServWorkflowResponse>(responseContent);
        }
        else
        {
            await HandleErrorResponseAsync(response, ref result);
        }
    }
    catch (Exception ex)
    {
        OASISErrorHandling.HandleError(ref result, 
            $"Error getting workflow status: {ex.Message}", ex);
    }
    
    return result;
}
```

### 2.5 Retry Logic Implementation

```csharp
/// <summary>
/// Execute HTTP request with exponential backoff retry logic
/// </summary>
private async Task<HttpResponseMessage> ExecuteWithRetryAsync(
    Func<Task<HttpResponseMessage>> requestFunc)
{
    int attempt = 0;
    TimeSpan delay = TimeSpan.FromSeconds(1);
    
    while (attempt < _maxRetries)
    {
        try
        {
            var response = await requestFunc();
            
            // Success or non-retryable error
            if (response.IsSuccessStatusCode || 
                response.StatusCode == HttpStatusCode.BadRequest ||
                response.StatusCode == HttpStatusCode.Unauthorized ||
                response.StatusCode == HttpStatusCode.NotFound)
            {
                return response;
            }
            
            // Retryable error
            if (response.StatusCode == HttpStatusCode.TooManyRequests ||
                response.StatusCode == HttpStatusCode.InternalServerError ||
                response.StatusCode == HttpStatusCode.ServiceUnavailable)
            {
                attempt++;
                
                if (attempt < _maxRetries)
                {
                    // Check for Retry-After header
                    if (response.Headers.Contains("Retry-After"))
                    {
                        var retryAfter = response.Headers.GetValues("Retry-After").FirstOrDefault();
                        if (int.TryParse(retryAfter, out var seconds))
                        {
                            delay = TimeSpan.FromSeconds(seconds);
                        }
                    }
                    else
                    {
                        // Exponential backoff with jitter
                        delay = TimeSpan.FromSeconds(Math.Pow(2, attempt) + 
                            new Random().Next(0, 1000) / 1000.0);
                    }
                    
                    _logger.LogWarning(
                        "Request failed with retryable error. Retrying in {Delay}ms. Attempt {Attempt}/{MaxRetries}",
                        delay.TotalMilliseconds, attempt, _maxRetries);
                    
                    await Task.Delay(delay);
                    continue;
                }
            }
            
            return response;
        }
        catch (HttpRequestException ex) when (attempt < _maxRetries)
        {
            attempt++;
            
            if (attempt < _maxRetries)
            {
                delay = TimeSpan.FromSeconds(Math.Pow(2, attempt) + 
                    new Random().Next(0, 1000) / 1000.0);
                
                _logger.LogWarning(ex,
                    "HTTP request exception. Retrying in {Delay}ms. Attempt {Attempt}/{MaxRetries}",
                    delay.TotalMilliseconds, attempt, _maxRetries);
                
                await Task.Delay(delay);
            }
            else
            {
                throw;
            }
        }
        catch (TaskCanceledException ex) when (attempt < _maxRetries)
        {
            attempt++;
            
            if (attempt < _maxRetries)
            {
                delay = TimeSpan.FromSeconds(Math.Pow(2, attempt));
                
                _logger.LogWarning(ex,
                    "Request timeout. Retrying in {Delay}ms. Attempt {Attempt}/{MaxRetries}",
                    delay.TotalMilliseconds, attempt, _maxRetries);
                
                await Task.Delay(delay);
            }
            else
            {
                throw;
            }
        }
    }
    
    throw new InvalidOperationException("Max retries exceeded");
}
```

### 2.6 Error Handling

```csharp
/// <summary>
/// Handle error responses from OpenSERV API
/// </summary>
private async Task HandleErrorResponseAsync(
    HttpResponseMessage response, 
    ref OASISResult result)
{
    var statusCode = response.StatusCode;
    var responseContent = await response.Content.ReadAsStringAsync();
    
    string errorMessage;
    string errorCode = statusCode.ToString();
    
    try
    {
        var errorResponse = JsonSerializer.Deserialize<OpenServErrorResponse>(responseContent);
        errorMessage = errorResponse?.Error?.Message ?? response.ReasonPhrase;
        errorCode = errorResponse?.Error?.Code ?? errorCode;
    }
    catch
    {
        errorMessage = response.ReasonPhrase ?? "Unknown error";
    }
    
    // Map HTTP status codes to meaningful error messages
    switch (statusCode)
    {
        case HttpStatusCode.BadRequest:
            errorMessage = $"Bad request: {errorMessage}";
            break;
        case HttpStatusCode.Unauthorized:
            errorMessage = "Unauthorized: Invalid API key";
            break;
        case HttpStatusCode.NotFound:
            errorMessage = $"Resource not found: {errorMessage}";
            break;
        case HttpStatusCode.TooManyRequests:
            errorMessage = "Rate limit exceeded. Please retry later.";
            break;
        case HttpStatusCode.InternalServerError:
            errorMessage = $"OpenSERV server error: {errorMessage}";
            break;
        case HttpStatusCode.ServiceUnavailable:
            errorMessage = "OpenSERV service unavailable. Please retry later.";
            break;
        default:
            errorMessage = $"HTTP {statusCode}: {errorMessage}";
            break;
    }
    
    result.ErrorCode = errorCode;
    OASISErrorHandling.HandleError(ref result, errorMessage);
    
    _logger.LogError(
        "OpenSERV API error: {StatusCode} - {ErrorMessage}",
        statusCode, errorMessage);
}
```

### 2.7 Webhook Signature Verification

```csharp
/// <summary>
/// Verify webhook signature from OpenSERV
/// </summary>
public bool VerifyWebhookSignature(string payload, string signature, string secret)
{
    try
    {
        if (string.IsNullOrEmpty(payload) || string.IsNullOrEmpty(signature))
        {
            return false;
        }
        
        // Extract signature from header format: "sha256={signature}"
        var signatureParts = signature.Split('=');
        if (signatureParts.Length != 2 || signatureParts[0] != "sha256")
        {
            return false;
        }
        
        var receivedSignature = signatureParts[1];
        
        // Compute HMAC-SHA256
        using (var hmac = new HMACSHA256(Encoding.UTF8.GetBytes(secret)))
        {
            var computedHash = hmac.ComputeHash(Encoding.UTF8.GetBytes(payload));
            var computedSignature = BitConverter.ToString(computedHash)
                .Replace("-", "")
                .ToLowerInvariant();
            
            // Constant-time comparison to prevent timing attacks
            return ConstantTimeEquals(receivedSignature.ToLowerInvariant(), computedSignature);
        }
    }
    catch (Exception ex)
    {
        _logger.LogError(ex, "Error verifying webhook signature");
        return false;
    }
}

/// <summary>
/// Constant-time string comparison to prevent timing attacks
/// </summary>
private bool ConstantTimeEquals(string a, string b)
{
    if (a.Length != b.Length)
    {
        return false;
    }
    
    int result = 0;
    for (int i = 0; i < a.Length; i++)
    {
        result |= a[i] ^ b[i];
    }
    
    return result == 0;
}
```

---

## 3. Request/Response Models

### 3.1 Agent Models

```csharp
namespace NextGenSoftware.OASIS.API.Core.Models.OpenServ
{
    /// <summary>
    /// Request model for registering an OpenSERV agent
    /// </summary>
    public class OpenServAgentRequest
    {
        [JsonPropertyName("agent_id")]
        public string AgentId { get; set; }
        
        [JsonPropertyName("name")]
        public string Name { get; set; }
        
        [JsonPropertyName("description")]
        public string Description { get; set; }
        
        [JsonPropertyName("endpoint")]
        public string Endpoint { get; set; }
        
        [JsonPropertyName("capabilities")]
        public List<string> Capabilities { get; set; } = new List<string>();
        
        [JsonPropertyName("metadata")]
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
    }
    
    /// <summary>
    /// Response model for agent registration
    /// </summary>
    public class OpenServAgentResponse
    {
        [JsonPropertyName("success")]
        public bool Success { get; set; }
        
        [JsonPropertyName("agent_id")]
        public string AgentId { get; set; }
        
        [JsonPropertyName("status")]
        public string Status { get; set; }
        
        [JsonPropertyName("webhook_url")]
        public string WebhookUrl { get; set; }
    }
    
    /// <summary>
    /// Agent status model
    /// </summary>
    public class OpenServAgentStatus
    {
        [JsonPropertyName("agent_id")]
        public string AgentId { get; set; }
        
        [JsonPropertyName("status")]
        public string Status { get; set; } // "online", "offline", "error"
        
        [JsonPropertyName("last_seen")]
        public DateTime? LastSeen { get; set; }
        
        [JsonPropertyName("endpoint")]
        public string Endpoint { get; set; }
    }
}
```

### 3.2 Workflow Models

```csharp
namespace NextGenSoftware.OASIS.API.Core.Models.OpenServ
{
    /// <summary>
    /// Request model for executing a workflow
    /// </summary>
    public class OpenServWorkflowRequest
    {
        [JsonPropertyName("workflow_id")]
        public string WorkflowId { get; set; }
        
        [JsonPropertyName("agent_id")]
        public string AgentId { get; set; }
        
        [JsonPropertyName("input")]
        public Dictionary<string, object> Input { get; set; } = new Dictionary<string, object>();
        
        [JsonPropertyName("context")]
        public Dictionary<string, object> Context { get; set; } = new Dictionary<string, object>();
    }
    
    /// <summary>
    /// Response model for workflow execution
    /// </summary>
    public class OpenServWorkflowResponse
    {
        [JsonPropertyName("workflow_id")]
        public string WorkflowId { get; set; }
        
        [JsonPropertyName("workflow_execution_id")]
        public string WorkflowExecutionId { get; set; }
        
        [JsonPropertyName("status")]
        public string Status { get; set; } // "running", "completed", "failed"
        
        [JsonPropertyName("result")]
        public object Result { get; set; }
        
        [JsonPropertyName("execution_time_ms")]
        public long? ExecutionTimeMs { get; set; }
        
        [JsonPropertyName("error_message")]
        public string ErrorMessage { get; set; }
        
        [JsonPropertyName("estimated_completion")]
        public DateTime? EstimatedCompletion { get; set; }
    }
}
```

### 3.3 Error Models

```csharp
namespace NextGenSoftware.OASIS.API.Core.Models.OpenServ
{
    /// <summary>
    /// Error response model from OpenSERV API
    /// </summary>
    public class OpenServErrorResponse
    {
        [JsonPropertyName("error")]
        public OpenServError Error { get; set; }
    }
    
    /// <summary>
    /// Error details
    /// </summary>
    public class OpenServError
    {
        [JsonPropertyName("code")]
        public string Code { get; set; }
        
        [JsonPropertyName("message")]
        public string Message { get; set; }
        
        [JsonPropertyName("details")]
        public Dictionary<string, object> Details { get; set; }
        
        [JsonPropertyName("timestamp")]
        public DateTime Timestamp { get; set; }
    }
}
```

### 3.4 Webhook Models

```csharp
namespace NextGenSoftware.OASIS.API.Core.Models.OpenServ
{
    /// <summary>
    /// Webhook payload from OpenSERV
    /// </summary>
    public class OpenServWebhookPayload
    {
        [JsonPropertyName("event")]
        public string Event { get; set; } // "workflow_request", "workflow_complete", etc.
        
        [JsonPropertyName("timestamp")]
        public DateTime Timestamp { get; set; }
        
        [JsonPropertyName("data")]
        public Dictionary<string, object> Data { get; set; } = new Dictionary<string, object>();
    }
}
```

---

## 4. Configuration

### 4.1 appsettings.json

```json
{
  "OpenServ": {
    "BaseUrl": "https://api.openserv.ai",
    "ApiKey": "", // Set via environment variable
    "WebhookSecret": "", // Set via environment variable
    "MaxRetries": 3,
    "TimeoutSeconds": 30,
    "EnableWebhookVerification": true
  }
}
```

### 4.2 Environment Variables

```bash
OpenServ__ApiKey=your-api-key-here
OpenServ__WebhookSecret=your-webhook-secret-here
```

### 4.3 Dependency Injection Setup

```csharp
// In Program.cs or Startup.cs
services.AddHttpClient<OpenServBridgeService>(client =>
{
    var baseUrl = configuration["OpenServ:BaseUrl"] ?? "https://api.openserv.ai";
    client.BaseAddress = new Uri(baseUrl);
    client.Timeout = TimeSpan.FromSeconds(
        int.Parse(configuration["OpenServ:TimeoutSeconds"] ?? "30"));
})
.ConfigurePrimaryHttpMessageHandler(() => new HttpClientHandler
{
    // Configure SSL/TLS if needed
})
.AddPolicyHandler(GetRetryPolicy());

services.AddScoped<OpenServBridgeService>();
```

---

## 5. Integration with A2A Protocol

### 5.1 A2AManager-OpenSERV Integration

The `A2AManager-OpenSERV.cs` will use `OpenServBridgeService` to:

1. Register OpenSERV agents as A2A agents
2. Route A2A messages to OpenSERV workflows
3. Transform responses back to A2A format

See `A2A_OPENSERV_INTEGRATION.md` for integration details.

---

## 6. Testing Strategy

### 6.1 Unit Tests

- Test HTTP client wrapper
- Test retry logic
- Test error handling
- Test webhook signature verification

### 6.2 Integration Tests

- Test agent registration (with mock server)
- Test workflow execution
- Test webhook handling

### 6.3 End-to-End Tests

- Register real agent
- Execute real workflow
- Verify results

---

## 7. Error Codes & Handling

### 7.1 Error Code Mapping

| OpenSERV Error | OASIS Error Code | Handling |
|---------------|------------------|----------|
| AGENT_NOT_FOUND | OPENSERV_AGENT_NOT_FOUND | Return error, don't retry |
| AGENT_OFFLINE | OPENSERV_AGENT_OFFLINE | Retry with backoff |
| INVALID_API_KEY | OPENSERV_AUTH_ERROR | Return error, don't retry |
| RATE_LIMIT_EXCEEDED | OPENSERV_RATE_LIMIT | Retry with exponential backoff |
| WORKFLOW_TIMEOUT | OPENSERV_TIMEOUT | Retry or return error |
| INVALID_WEBHOOK_SIGNATURE | OPENSERV_WEBHOOK_ERROR | Return error, log security issue |

---

## 8. Performance Considerations

### 8.1 HTTP Client Reuse

- Use `IHttpClientFactory` for proper HTTP client lifecycle
- Reuse HTTP client instances
- Configure connection pooling

### 8.2 Timeout Configuration

- Default timeout: 30 seconds
- Configurable per operation
- Separate timeouts for sync vs async operations

### 8.3 Caching

- Cache agent status (with TTL)
- Cache workflow results (if applicable)
- Use appropriate cache invalidation

---

## 9. Security Considerations

### 9.1 API Key Security

- Never log API keys
- Store in secure configuration
- Rotate keys periodically

### 9.2 Webhook Security

- Always verify signatures
- Use HTTPS for webhook endpoints
- Implement rate limiting

### 9.3 Request Validation

- Validate all input parameters
- Sanitize user input
- Prevent injection attacks

---

## 10. Logging & Monitoring

### 10.1 Logging

- Log all API calls (without sensitive data)
- Log errors with full context
- Log retry attempts
- Log webhook events

### 10.2 Metrics

- Track API call counts
- Track error rates
- Track response times
- Track retry counts

---

## 11. Future Enhancements

1. **Connection Pooling:** Optimize HTTP client connections
2. **Circuit Breaker:** Implement circuit breaker pattern
3. **Caching:** Add response caching for frequently accessed data
4. **Metrics:** Add detailed metrics and telemetry
5. **Health Checks:** Implement health check endpoints

---

## 12. Files to Create

1. `ONODE/NextGenSoftware.OASIS.API.ONODE.WebAPI/Services/OpenServBridgeService.cs`
2. `OASIS Architecture/NextGenSoftware.OASIS.API.Core/Models/OpenServ/OpenServAgentRequest.cs`
3. `OASIS Architecture/NextGenSoftware.OASIS.API.Core/Models/OpenServ/OpenServAgentResponse.cs`
4. `OASIS Architecture/NextGenSoftware.OASIS.API.Core/Models/OpenServ/OpenServWorkflowRequest.cs`
5. `OASIS Architecture/NextGenSoftware.OASIS.API.Core/Models/OpenServ/OpenServWorkflowResponse.cs`
6. `OASIS Architecture/NextGenSoftware.OASIS.API.Core/Models/OpenServ/OpenServErrorResponse.cs`
7. `OASIS Architecture/NextGenSoftware.OASIS.API.Core/Models/OpenServ/OpenServWebhookPayload.cs`

---

## 13. References

- **OpenSERV API Research:** `/A2A/docs/OPENSERV_API_RESEARCH.md`
- **A2A Integration Doc:** `/A2A/docs/A2A_OPENSERV_INTEGRATION.md`
- **OASISResult Pattern:** `OASIS Architecture/NextGenSoftware.OASIS.Common/OASISResult.cs`
- **Error Handling:** `OASIS Architecture/NextGenSoftware.OASIS.Common/OASISErrorHandling.cs`

---

**Last Updated:** January 5, 2026  
**Status:** ✅ Design Complete - Ready for Implementation

