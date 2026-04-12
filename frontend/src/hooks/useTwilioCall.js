import { useState, useCallback, useRef, useEffect } from 'react'
import { Device } from '@twilio/voice-sdk'

export function useTwilioCall() {
    const [callStatus, setCallStatus] = useState('idle') // idle, connecting, ringing, active, error, completed
    const [error, setError] = useState(null)
    const deviceRef = useRef(null)
    const callRef = useRef(null)

    const cleanup = useCallback(() => {
        if (callRef.current) {
            callRef.current.disconnect()
            callRef.current = null
        }
        if (deviceRef.current) {
            deviceRef.current.destroy()
            deviceRef.current = null
        }
    }, [])

    useEffect(() => {
        return cleanup
    }, [cleanup])

    const initiateCall = useCallback(async (phoneNumber) => {
        try {
            setCallStatus('connecting')
            setError(null)

            // Step 1: Request Microphone Access proactively
            await navigator.mediaDevices.getUserMedia({ audio: true })

            // Step 2: Fetch Token (Mocked)
            // In production, this would be: await fetch('/api/twilio-token').then(r => r.json())
            const mockToken = 'MOCK_TOKEN_' + Math.random().toString(36).substr(2)

            // Step 3: Initialize Device
            const device = new Device(mockToken, {
                codecPreferences: ['opus', 'pcmu'],
                fakeLocalAudio: true, // For development/mocking purposes
                enableIceRestart: true
            })

            deviceRef.current = device

            // Step 4: Event Listeners
            device.on('registered', () => {
                console.log('Twilio Device Registered')
                // Step 5: Connect Outbound
                const call = device.connect({
                    params: {
                        To: phoneNumber,
                        From: 'AdmissionsBot'
                    }
                })
                callRef.current = call

                call.on('accept', () => setCallStatus('active'))
                call.on('disconnect', () => setCallStatus('completed'))
                call.on('error', (err) => {
                    setError(err.message)
                    setCallStatus('error')
                })
            })

            device.on('error', (err) => {
                console.warn('Twilio Device Error:', err)
                // Fallback simulation for signaling errors (e.g. invalid tokens)
                if (err && (err.message?.includes('Token') || err.message?.includes('Signaling') || err.code === 20101)) {
                    console.info('Entering simulated call mode...')
                    setTimeout(() => setCallStatus('active'), 2000)
                    return
                }
                setError(err?.message || 'Device registration failed')
                setCallStatus('error')
            })

            await device.register()

        } catch (err) {
            console.error('Telephony Error Exception:', err)

            // Catch synchronous errors or permission denials
            const errorMsg = err?.name === 'NotAllowedError' ? 'Microphone access denied' : (err?.message || 'Initialization failed')

            // Even if the try block fails, we try to simulate for the demo
            if (errorMsg.includes('Token') || errorMsg.includes('MOCK')) {
                console.info('Simulating call after catch...')
                setTimeout(() => setCallStatus('active'), 2000)
                return
            }

            setError(errorMsg)
            setCallStatus('error')
        }
    }, [])

    const endCall = useCallback(() => {
        if (callRef.current) {
            callRef.current.disconnect()
        }
        setCallStatus('completed')
    }, [])

    return { initiateCall, endCall, callStatus, error }
}
