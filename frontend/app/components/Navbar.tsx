import {Upload, Bot} from 'lucide-react';
import UploadPanel from './UploadPanel';

export default function Navbar() {
  return (
    <header className="h-16 border-b border-slate-800 flex items-center justify-between px-6">
      <div className='text-xl font-bold'>
        Code Architect
      </div>
      <div className='flex items-center gap-3'>
        <button className="flex items-center gap-2 rounded-lg bg-blue-600 hover:bg-blue-700 px-4 py-2 text-sm font-medium transition">

          <UploadPanel/>

          Upload Repository

        </button>
        <button className="rounded-lg border border-slate-700 p-2 hover:bg-slate-800">

          <Bot size={18} />

        </button>
      </div>
    </header>
  );
}