"use client";

import { useState } from "react";
import { useRepository } from "../context/RepositoryContext";
import api from "../../lib/api";
import ChatInput from "./ChatInput";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";

type Message = {
    role: "user" | "assistant";
    content: string;
};

export default function AgentPanel() {

    const { repository } = useRepository();

    const [messages, setMessages] = useState<Message[]>([]);
    const [loading, setLoading] = useState(false);
    const [pdfAvailable, setPdfAvailable] = useState(false);
    const clearChat = () => {
    setMessages([]);
    setPdfAvailable(false);
};
    
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
            console.log(response.data);
            if (response.data.agent === "documentation") {
    setPdfAvailable(true);
}
            setMessages(prev => [
                ...prev,
                {
                    role: "assistant",
                    content:
    typeof response.data.answer === "string"
        ? response.data.answer
        : response.data.answer.answer,
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

                             {message.role === "user" ? (
        message.content
    ) : (
        <Markdown
            remarkPlugins={[remarkGfm]}
        >
            {message.content}
        </Markdown>
    )}

                        </div>

                    </div>

                ))}

                {loading && (
                    <p className="text-slate-400">
                        Thinking...
                    </p>
                )}

            </div>
            <div className="border-t border-slate-800 p-3 space-y-2">

    {pdfAvailable && (
       <a
    href={`${process.env.NEXT_PUBLIC_API_URL}/api/chat/download/${repository?.repository_id}`}
    download
    className="w-full rounded bg-green-600 px-4 py-2 font-medium text-white hover:bg-green-700 inline-block text-center"
>
    Download Documentation PDF
</a>
    )}

    <button
        onClick={clearChat}
        className="w-full rounded bg-slate-700 px-4 py-2 font-medium text-white hover:bg-slate-600"
    >
        Clear Chat
    </button>

</div>
            <ChatInput onSend={sendMessage} />

        </div>
    );
}
