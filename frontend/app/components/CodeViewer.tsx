"use client";

import Editor from "@monaco-editor/react";
import { useEffect, useState } from "react";
import api from "../../lib/api";
import { useRepository } from "../context/RepositoryContext";

export default function CodeViewer() {
console.log("CodeViewer rendered");
    const {
        repository,
        selectedFile
    } = useRepository();

    const [code, setCode] = useState("");

    useEffect(() => {

    console.log("Repository:", repository);
    console.log("Selected file:", selectedFile);

    if (!repository || !selectedFile) return;

    api.get(
        `/api/file/${repository.repository_id}`,
        {
            params: {
                path: selectedFile
            }
        }
    ).then(res => {

        console.log("Response:", res.data);

        setCode(res.data.content);

    });

}, [repository, selectedFile]);

    return (

        <Editor
            height="100%"
            theme="vs-dark"
            value={code}
            language="python"
            options={{
                readOnly: true,
                minimap: {
                    enabled: false
                },
                fontSize: 14,
                scrollBeyondLastLine: false
            }}
        />

    );

}