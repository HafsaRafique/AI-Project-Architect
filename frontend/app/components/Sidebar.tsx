"use client";

import { useRepository } from "../context/RepositoryContext";

export default function Sidebar() {

    const { repository } = useRepository();

    return (

        <div className="p-4">

            <h2 className="font-bold">
                Repository
            </h2>

            <pre className="mt-4 text-xs overflow-auto">

                {JSON.stringify(repository, null, 2)}

            </pre>

        </div>

    );

}