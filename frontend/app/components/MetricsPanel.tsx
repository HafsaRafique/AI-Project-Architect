"use client";

import { useRepository } from "../context/RepositoryContext";

export default function MetricsPanel() {

    const { repository } = useRepository();
    console.log(repository);
    const metrics = repository?.analysis?.metrics;
    const summary = repository?.analysis?.summary;

    if (!metrics || !summary) {
        return (
            <div className="p-6 text-slate-400">
                No repository loaded.
            </div>
        );
    }

    const cards = [
        { title: "Files", value: summary.total_files },
        { title: "Functions", value: summary.total_functions },
        { title: "Classes", value: summary.total_classes },
        { title: "Modules", value: summary.total_modules },
        { title: "Avg Func/File", value: metrics.average_functions_per_file },
        { title: "Avg Class/File", value: metrics.average_classes_per_file },
        { title: "Largest File", value: metrics.largest_file },
        { title: "Most Imports", value: metrics.most_imported_file }
    ];

    return (

        <div className="grid grid-cols-2 gap-4 p-4">

            {cards.map((card) => (

                <div
                    key={card.title}
                    className="rounded-lg border border-slate-800 bg-slate-900 p-4"
                >
                    <p className="text-xs text-slate-400">
                        {card.title}
                    </p>

                    <p className="mt-2 text-lg font-semibold text-white break-all">
                        {card.value}
                    </p>

                </div>

            ))}

        </div>

    );

}