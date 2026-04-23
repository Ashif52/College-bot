import { createMachine, assign } from 'xstate'

const generateId = () => `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

export const chatMachine = createMachine({
    id: 'edubot',
    initial: 'idle',
    context: {
        userName: '',
        userPhone: '',
        messages: [],
    },
    states: {
        idle: {
            on: {
                OPEN_CHAT: 'greeting',
            },
        },
        greeting: {
            entry: assign({
                messages: ({ context }) => [
                    ...context.messages,
                    { id: generateId(), text: "Hi! I'm EduBot, your Nexus admissions assistant. How can I help you today?", sender: 'bot' }
                ]
            }),
            on: {
                SELECT_FAQ: 'answering_faq',
                REQUEST_CALL: 'collecting_name',
            },
        },
        answering_faq: {
            entry: assign({
                messages: ({ context, event }) => [
                    ...context.messages,
                    { id: generateId(), text: event.question, sender: 'user' },
                    { id: generateId(), text: event.answer, sender: 'bot' }
                ]
            }),
            on: {
                RETURN_TO_MENU: 'greeting',
                REQUEST_CALL: 'collecting_name',
            },
        },
        collecting_name: {
            entry: assign({
                messages: ({ context }) => [
                    ...context.messages,
                    { id: generateId(), text: "I'd be happy to arrange a call! First, please provide your full name.", sender: 'bot' }
                ]
            }),
            on: {
                SUBMIT_NAME: {
                    target: 'collecting_phone',
                    actions: assign({
                        userName: ({ event }) => event.name,
                        messages: ({ context, event }) => [
                            ...context.messages,
                            { id: generateId(), text: event.name, sender: 'user' }
                        ]
                    }),
                    guard: ({ event }) => event.name.length >= 2,
                },
            },
        },
        collecting_phone: {
            entry: assign({
                messages: ({ context }) => [
                    ...context.messages,
                    { id: generateId(), text: `Thanks ${context.userName}! What is your 10-digit mobile number?`, sender: 'bot' }
                ]
            }),
            on: {
                SUBMIT_PHONE: {
                    target: 'initiating_call',
                    actions: assign({
                        userPhone: ({ event }) => event.phone,
                        messages: ({ context, event }) => [
                            ...context.messages,
                            { id: generateId(), text: event.phone, sender: 'user' }
                        ]
                    }),
                    guard: ({ event }) => /^\d{10}$/.test(event.phone),
                },
            },
        },
        initiating_call: {
            entry: assign({
                messages: ({ context }) => [
                    ...context.messages,
                    { id: generateId(), text: "Perfect. I'm connecting your call to our admissions office now. Please keep your browser open and grant microphone access if prompted!", sender: 'bot' }
                ]
            }),
            on: {
                CALL_CONNECTED: 'active_call',
                CALL_FAILED: 'error_state',
            },
        },
        active_call: {
            on: {
                END_CALL: 'call_completed',
            },
        },
        error_state: {
            entry: assign({
                messages: ({ context }) => [
                    ...context.messages,
                    { id: generateId(), text: "I'm sorry, I encountered an error while trying to connect the call. You can reach us directly at admissions@nexus.ac.in", sender: 'bot' }
                ]
            }),
            on: {
                RETRY: 'greeting',
            },
        },
        call_completed: {
            entry: assign({
                messages: ({ context }) => [
                    ...context.messages,
                    { id: generateId(), text: "Thank you for reaching out! A counselor has been notified about your interest. Have a great day!", sender: 'bot' }
                ]
            }),
            on: {
                RESET_CHAT: 'greeting',
            },
        },
    },
})
