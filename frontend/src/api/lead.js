/**
 * Lead API Module
 * Handles submission of admission leads and auto-call triggers.
 * Currently simulates API responses for development.
 * Ready for integration with Twilio, Exotel, or Knowlarity.
 */

/**
 * Submit an admission lead to the backend
 * @param {Object} data - { name, phone, email }
 * @returns {Promise<Object>} - { success, message, leadId }
 */
export async function submitLead(data) {
    // Simulate API call: POST /api/admission-lead
    console.log('📋 Submitting lead:', {
        ...data,
        source: 'chatbot',
        timestamp: new Date().toISOString(),
    })

    // Simulate network delay
    await new Promise((resolve) => setTimeout(resolve, 800))

    // In production, replace with:
    // const response = await fetch('/api/admission-lead', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({ ...data, source: 'chatbot' }),
    // })
    // return response.json()

    return {
        success: true,
        message: 'Lead submitted successfully',
        leadId: `LEAD-${Date.now()}`,
    }
}

/**
 * Trigger an automatic call to the lead
 * Future integration with Twilio / Exotel / Knowlarity
 * @param {string} phone - Phone number to call
 * @returns {Promise<Object>} - { success, message, callId }
 */
export async function triggerAutoCall(phone) {
    console.log('📞 Triggering auto-call to:', phone)

    // Simulate network delay
    await new Promise((resolve) => setTimeout(resolve, 500))

    // Twilio integration placeholder:
    // const client = require('twilio')(accountSid, authToken)
    // const call = await client.calls.create({
    //   url: 'https://your-server.com/twiml',
    //   to: phone,
    //   from: '+91XXXXXXXXXX',
    // })

    // Exotel integration placeholder:
    // const response = await fetch('https://api.exotel.com/v1/Accounts/{SID}/Calls/connect', {
    //   method: 'POST',
    //   body: new URLSearchParams({
    //     From: phone,
    //     To: '+91XXXXXXXXXX',
    //     CallerId: 'XXXXXXXXXX',
    //     Url: 'https://your-server.com/exotel-flow',
    //   }),
    // })

    // Knowlarity integration placeholder:
    // const response = await fetch('https://kpi.knowlarity.com/Basic/v1/account/call/makecall', {
    //   method: 'POST',
    //   headers: {
    //     'x-]api-key': 'YOUR_API_KEY',
    //     'Authorization': 'YOUR_AUTH',
    //   },
    //   body: JSON.stringify({
    //     k_number: '+91XXXXXXXXXX',
    //     agent_number: '+91XXXXXXXXXX',
    //     customer_number: phone,
    //   }),
    // })

    return {
        success: true,
        message: 'Call request queued successfully',
        callId: `CALL-${Date.now()}`,
    }
}
