"use client";
import { Upload } from "lucide-react";
import api from "@/lib/api";
import { ReactEventHandler } from "react";
import { Console } from "console";
import { useState } from "react";
import { useRepository } from "../context/RepositoryContext";


export default function UploadPanel(){

    const {setRepository} = useRepository();

      const [url, setUrl] = useState("");

    async function handleUpload(e:React.ChangeEvent<HTMLInputElement>) {
        const file = e.target.files?.[0];
        if (!file) return;
        
        const formData = new FormData();
        formData.append("file", file);

        const response = await api.post(
            "/apiupload",
            formData
        );
        

        
        setRepository(response.data);

    }

    async function handleURLUpload(){


        if(!url) return;



        const response = await api.post(
            "/apiupload/url",
            {
                url:url
            }
        );


        setRepository(
            response.data
        );


    }
    return(

        <label className="cursor-pointer flex items-center gap-2 rounded-lg bg-blue-600 hover:bg-blue-700 px-4 py-2">

            <Upload size={18}/>

            Upload Repository

            <input hidden type='file' accept ='.zip' onChange={handleUpload}/>

    </label>
    );
}
