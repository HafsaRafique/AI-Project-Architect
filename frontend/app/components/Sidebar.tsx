"use client";

import { useRepository } from "../context/RepositoryContext";

import RepositoryTree from "./RepositoryTree";

export default function Sidebar() {

    const { repository } = useRepository();

    return (

        <div className="p-4">

            <h2 className="font-bold">
                Repository
            </h2>

            <RepositoryTree/>

        </div>

    );

}