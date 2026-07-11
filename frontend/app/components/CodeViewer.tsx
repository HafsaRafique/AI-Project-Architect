"use client";

import { useEffect, useState } from "react";
import api from "../../lib/api";
import { useRepository } from "../context/RepositoryContext";

export default function CodeViewer() {

    const {
        repository,
        selectedFile
    } = useRepository();

    const [code, setCode] = useState("");

    useEffect(() => {

        if (!repository || !selectedFile)
            return;

        api.get(
            `/api/file/${repository.repository_id}`,
            {
                params: {
                    path: selectedFile
                }
            }
        )
        .then(res => setCode(res.data.content));

    }, [
        repository,
        selectedFile
    ]);

    return (

        <pre className="h-full overflow-auto p-6 text-sm">

            <code>

                {code}

            </code>

        </pre>

    );

}