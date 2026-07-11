"use client";

import { useState } from "react";
import { useRepository } from "../context/RepositoryContext";
import api from "../../lib/api";
import ChatInput from "./ChatInput";

type Message = {
    role: "user" | "assistant";
    content: string;
};

export default function AgentPanel() {

    const { repository } = useRepository();

    const [messages, setMessages] = useState<Message[]>([]);
    const [loading, setLoading] = useState(false);

    async function sendMessage(question: string) {

        if (!repository) return;

        setMessages(prev => [
            ...prev,
            {
                role: "user",
                content: question,
            },
        ]);

        setLoading(true);

        try {

            const response = await api.post(
                "/api/chat",
                {
                    repository_id: repository.repository_id,
                    question: question,
                }
            );

            setMessages(prev => [
                ...prev,
                {
                    role: "assistant",
                    content: response.data.answer.answer,
                },
            ]);

        } catch (err) {

            console.error(err);

        } finally {

            setLoading(false);

        }
    }

    return (
        <div className="flex flex-col h-full">

            <div className="flex-1 overflow-y-auto p-4 space-y-4">

                {messages.map((message, index) => (

                    <div
                        key={index}
                        className={
                            message.role === "user"
                                ? "text-right"
                                : "text-left"
                        }
                    >

                        <div
                            className={
                                message.role === "user"
                                    ? "inline-block rounded-lg bg-blue-600 px-3 py-2"
                                    : "inline-block rounded-lg bg-slate-800 px-3 py-2"
                            }
                        >

                            {message.content}

                        </div>

                    </div>

                ))}

                {loading && (
                    <p className="text-slate-400">
                        Thinking...
                    </p>
                )}

            </div>

            <ChatInput onSend={sendMessage} />

        </div>
    );
}