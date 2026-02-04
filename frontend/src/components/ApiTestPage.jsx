import { useState } from 'react';

const ApiTestPage = () => {
  const [endpoint, setEndpoint] = useState('http://localhost:8000');
  const [requestType, setRequestType] = useState('capacity_query');
  const [location, setLocation] = useState('Downtown');
  const [reason, setReason] = useState('Testing backend integration');
  const [estimatedCost, setEstimatedCost] = useState('');
  const [customFields, setCustomFields] = useState('');
  
  const [jobId, setJobId] = useState('');
  const [loading, setLoading] = useState(false);
  const [polling, setPolling] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [logs, setLogs] = useState([]);
  
  const addLog = (message, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, { timestamp, message, type }]);
  };

  const requestTypes = {
    water: [
      'capacity_query',
      'schedule_shift_request',
      'emergency_response',
      'maintenance_request',
      'pipeline_repair',
      'water_quality_check'
    ],
    engineering: [
      'project_planning',
      'infrastructure_assessment',
      'road_repair',
      'bridge_inspection',
      'construction_approval'
    ],
    fire: [
      'fire_emergency',
      'fire_inspection',
      'fire_safety_assessment',
      'hazmat_response',
      'rescue_operation'
    ],
    sanitation: [
      'waste_collection',
      'street_cleaning',
      'sanitation_inspection',
      'recycling_request',
      'hazardous_waste_disposal'
    ],
    health: [
      'health_inspection',
      'disease_outbreak',
      'vaccination_campaign',
      'restaurant_inspection',
      'public_health_assessment'
    ],
    finance: [
      'budget_approval',
      'cost_estimation',
      'financial_audit',
      'revenue_forecast',
      'expenditure_review'
    ]
  };

  const submitQuery = async () => {
    setLoading(true);
    setError(null);
    setResponse(null);
    setJobId('');
    addLog('Submitting query to backend...', 'info');

    try {
      const payload = {
        type: requestType,
        location: location,
        reason: reason,
        from: 'Frontend Test Page'
      };

      if (estimatedCost) {
        payload.estimated_cost = parseFloat(estimatedCost);
      }

      // Add custom fields if provided
      if (customFields) {
        try {
          const custom = JSON.parse(customFields);
          Object.assign(payload, custom);
        } catch (e) {
          addLog('Invalid JSON in custom fields, ignoring', 'warning');
        }
      }

      addLog(`Request: ${JSON.stringify(payload, null, 2)}`, 'info');

      const res = await fetch(`${endpoint}/api/v1/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }

      const data = await res.json();
      addLog(`Query submitted successfully!`, 'success');
      addLog(`Job ID: ${data.job_id}`, 'success');
      addLog(`Routed to: ${data.agent_type} agent`, 'info');
      
      setJobId(data.job_id);
      setResponse(data);
      
      // Auto-start polling
      startPolling(data.job_id);
      
    } catch (err) {
      addLog(`Error: ${err.message}`, 'error');
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const startPolling = async (id) => {
    const pollJobId = id || jobId;
    if (!pollJobId) {
      addLog('No job ID to poll', 'error');
      return;
    }

    setPolling(true);
    addLog('Starting to poll for results...', 'info');

    let attempts = 0;
    const maxAttempts = 30;

    const poll = async () => {
      if (attempts >= maxAttempts) {
        addLog('Polling timeout (60 seconds)', 'error');
        setPolling(false);
        return;
      }

      attempts++;
      addLog(`Polling attempt ${attempts}/${maxAttempts}...`, 'info');

      try {
        const res = await fetch(`${endpoint}/api/v1/query/${pollJobId}`);
        
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }

        const data = await res.json();
        addLog(`Status: ${data.status}`, 'info');

        if (data.status === 'succeeded') {
          addLog('✅ Job completed successfully!', 'success');
          setResponse(data);
          setPolling(false);
          return;
        } else if (data.status === 'failed') {
          addLog(`❌ Job failed: ${data.error}`, 'error');
          setResponse(data);
          setPolling(false);
          return;
        } else {
          // Still running, poll again
          setTimeout(poll, 2000);
        }
      } catch (err) {
        addLog(`Polling error: ${err.message}`, 'error');
        setPolling(false);
      }
    };

    poll();
  };

  const checkHealth = async () => {
    addLog('Checking backend health...', 'info');
    try {
      const res = await fetch(`${endpoint}/api/v1/health`);
      const data = await res.json();
      
      if (data.status === 'ok') {
        addLog(`✅ Backend healthy`, 'success');
        addLog(`Coordinator: ${data.coordinator}`, 'info');
        addLog(`Version: ${data.version}`, 'info');
      } else {
        addLog('⚠️ Backend returned unhealthy status', 'warning');
      }
    } catch (err) {
      addLog(`❌ Health check failed: ${err.message}`, 'error');
    }
  };

  const clearLogs = () => {
    setLogs([]);
  };

  const getDepartment = (type) => {
    for (const [dept, types] of Object.entries(requestTypes)) {
      if (types.includes(type)) {
        return dept;
      }
    }
    return 'water';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-white mb-4">
            Backend API Test Console
          </h1>
          <p className="text-xl text-blue-200">
            Test the complete flow: Frontend → Backend → Coordinator → Agents
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Panel - Request Configuration */}
          <div className="space-y-6">
            {/* Endpoint Configuration */}
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <h2 className="text-2xl font-bold text-white mb-4">Endpoint Configuration</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-blue-200 mb-2">
                    Backend URL
                  </label>
                  <input
                    type="text"
                    value={endpoint}
                    onChange={(e) => setEndpoint(e.target.value)}
                    className="w-full px-4 py-2 bg-white/5 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="http://localhost:8000"
                  />
                </div>

                <button
                  onClick={checkHealth}
                  className="w-full px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-colors"
                >
                  🏥 Check Health
                </button>
              </div>
            </div>

            {/* Request Builder */}
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <h2 className="text-2xl font-bold text-white mb-4">Request Builder</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-blue-200 mb-2">
                    Request Type
                  </label>
                  <select
                    value={requestType}
                    onChange={(e) => setRequestType(e.target.value)}
                    className="w-full px-4 py-2 bg-white/5 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {Object.entries(requestTypes).map(([dept, types]) => (
                      <optgroup key={dept} label={dept.toUpperCase()}>
                        {types.map(type => (
                          <option key={type} value={type}>{type}</option>
                        ))}
                      </optgroup>
                    ))}
                  </select>
                  <p className="mt-2 text-sm text-blue-300">
                    Will route to: <span className="font-bold text-yellow-300">{getDepartment(requestType)}</span> agent
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-blue-200 mb-2">
                    Location
                  </label>
                  <input
                    type="text"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    className="w-full px-4 py-2 bg-white/5 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Downtown"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-blue-200 mb-2">
                    Reason
                  </label>
                  <input
                    type="text"
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                    className="w-full px-4 py-2 bg-white/5 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Testing backend integration"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-blue-200 mb-2">
                    Estimated Cost (optional)
                  </label>
                  <input
                    type="number"
                    value={estimatedCost}
                    onChange={(e) => setEstimatedCost(e.target.value)}
                    className="w-full px-4 py-2 bg-white/5 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="50000"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-blue-200 mb-2">
                    Custom Fields (JSON)
                  </label>
                  <textarea
                    value={customFields}
                    onChange={(e) => setCustomFields(e.target.value)}
                    className="w-full px-4 py-2 bg-white/5 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                    placeholder='{"custom_field": "value"}'
                    rows="3"
                  />
                </div>

                <button
                  onClick={submitQuery}
                  disabled={loading || polling}
                  className="w-full px-6 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-600 disabled:to-gray-700 text-white font-bold text-lg rounded-lg transition-all transform hover:scale-105 disabled:scale-100"
                >
                  {loading ? '⏳ Submitting...' : '🚀 Submit Query'}
                </button>

                {jobId && (
                  <button
                    onClick={() => startPolling()}
                    disabled={polling}
                    className="w-full px-6 py-3 bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-600 text-white font-semibold rounded-lg transition-colors"
                  >
                    {polling ? '⏳ Polling...' : '🔄 Poll for Results'}
                  </button>
                )}
              </div>
            </div>

            {/* Response Display */}
            {response && (
              <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
                <h2 className="text-2xl font-bold text-white mb-4">Response</h2>
                
                <div className="space-y-4">
                  {response.job_id && (
                    <div>
                      <span className="text-blue-300 font-semibold">Job ID:</span>
                      <p className="text-white font-mono text-sm mt-1">{response.job_id}</p>
                    </div>
                  )}

                  {response.agent_type && (
                    <div>
                      <span className="text-blue-300 font-semibold">Agent Type:</span>
                      <p className="text-yellow-300 font-bold mt-1">{response.agent_type}</p>
                    </div>
                  )}

                  {response.status && (
                    <div>
                      <span className="text-blue-300 font-semibold">Status:</span>
                      <p className={`font-bold mt-1 ${
                        response.status === 'succeeded' ? 'text-green-400' :
                        response.status === 'failed' ? 'text-red-400' :
                        'text-yellow-400'
                      }`}>
                        {response.status.toUpperCase()}
                      </p>
                    </div>
                  )}

                  {response.result && (
                    <div>
                      <span className="text-blue-300 font-semibold">Decision:</span>
                      <div className="mt-2 p-4 bg-black/30 rounded-lg">
                        <p className="text-white">
                          <span className="font-bold">Type:</span> {response.result.decision}
                        </p>
                        {response.result.reason && (
                          <p className="text-white mt-2">
                            <span className="font-bold">Reason:</span> {response.result.reason}
                          </p>
                        )}
                        {response.result.requires_human_review !== undefined && (
                          <p className="text-white mt-2">
                            <span className="font-bold">Human Review:</span> {response.result.requires_human_review ? 'Yes' : 'No'}
                          </p>
                        )}
                        {response.result.details && (
                          <div className="mt-2">
                            <p className="font-bold text-white">Details:</p>
                            <p className="text-blue-200">
                              Feasible: {response.result.details.feasible ? 'Yes' : 'No'}
                            </p>
                            <p className="text-blue-200">
                              Policy Compliant: {response.result.details.policy_compliant ? 'Yes' : 'No'}
                            </p>
                            <p className="text-blue-200">
                              Confidence: {(response.result.details.confidence * 100).toFixed(0)}%
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  <details className="mt-4">
                    <summary className="text-blue-300 font-semibold cursor-pointer hover:text-blue-200">
                      Full JSON Response
                    </summary>
                    <pre className="mt-2 p-4 bg-black/50 rounded-lg text-xs text-green-400 overflow-auto max-h-96">
                      {JSON.stringify(response, null, 2)}
                    </pre>
                  </details>
                </div>
              </div>
            )}
          </div>

          {/* Right Panel - Logs */}
          <div>
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 h-full flex flex-col">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold text-white">Activity Logs</h2>
                <button
                  onClick={clearLogs}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-semibold rounded-lg transition-colors"
                >
                  Clear Logs
                </button>
              </div>
              
              <div className="flex-1 bg-black/50 rounded-lg p-4 overflow-auto font-mono text-sm space-y-2">
                {logs.length === 0 ? (
                  <p className="text-gray-400 italic">No logs yet. Submit a query to see activity...</p>
                ) : (
                  logs.map((log, idx) => (
                    <div key={idx} className={`${
                      log.type === 'error' ? 'text-red-400' :
                      log.type === 'success' ? 'text-green-400' :
                      log.type === 'warning' ? 'text-yellow-400' :
                      'text-blue-300'
                    }`}>
                      <span className="text-gray-500">[{log.timestamp}]</span> {log.message}
                    </div>
                  ))
                )}
              </div>

              {polling && (
                <div className="mt-4 p-4 bg-yellow-900/30 border border-yellow-600 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="animate-spin h-5 w-5 border-2 border-yellow-400 border-t-transparent rounded-full"></div>
                    <span className="text-yellow-300 font-semibold">Polling for results...</span>
                  </div>
                </div>
              )}

              {error && (
                <div className="mt-4 p-4 bg-red-900/30 border border-red-600 rounded-lg">
                  <p className="text-red-300 font-semibold">❌ Error:</p>
                  <p className="text-red-200 text-sm mt-1">{error}</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8 bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
          <h3 className="text-xl font-bold text-white mb-4">Quick Test Scenarios</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button
              onClick={() => {
                setRequestType('capacity_query');
                setLocation('Downtown');
                setReason('Quick water test');
                setEstimatedCost('');
              }}
              className="px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            >
              💧 Water Query
            </button>
            <button
              onClick={() => {
                setRequestType('project_planning');
                setLocation('Main Street');
                setReason('Road repair test');
                setEstimatedCost('50000');
              }}
              className="px-4 py-3 bg-orange-600 hover:bg-orange-700 text-white rounded-lg transition-colors"
            >
              🏗️ Engineering Query
            </button>
            <button
              onClick={() => {
                setRequestType('fire_inspection');
                setLocation('Industrial Zone');
                setReason('Safety inspection test');
                setEstimatedCost('');
              }}
              className="px-4 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
            >
              🚒 Fire Query
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ApiTestPage;
