"use client";

import { useState } from "react";

export default function ChatInput({

    onSend,

}:{

    onSend:(message:string)=>void

}){

    const [message,setMessage]=useState("");

    return(

        <div className="border-t border-slate-800 p-4">

            <textarea

                value={message}

                onChange={(e)=>setMessage(e.target.value)}

                className="w-full rounded-lg bg-slate-900 p-3 resize-none outline-none"

                rows={3}

                placeholder="Ask anything about the repository..."

            />

            <button

                onClick={()=>{

                    onSend(message);

                    setMessage("");

                }}

                className="mt-3 rounded bg-blue-600 px-4 py-2"

            >

                Send

            </button>

        </div>

    );

}