"use client";
import {
    createContext,
    useContext,
    useState,
    ReactNode,
} from "react";

type RepositoryData = {
    repository_id: string;
    tree: any[];
    analysis: any;
    graph: any;
};

type RepositoryContextType = {
    repository: RepositoryData | null;
    setRepository: (repo:RepositoryData) => void;
};

const RepositoryContext = createContext<RepositoryContextType | undefined>(undefined);

export function RepositoryProvider({children}:{children: ReactNode})
{
const [repository, setRepository] = useState<RepositoryData | null>(null);
return (
        <RepositoryContext.Provider value={{ repository, setRepository,}}>
            {children}
        </RepositoryContext.Provider>
    );
}

export function useRepository() {

    const context = useContext(
        RepositoryContext
    );

    if (!context) {
        throw new Error(
            "useRepository must be used inside RepositoryProvider"
        );
    }

    return context;
}

