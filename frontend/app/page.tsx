import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import ChatPanel from './components/ChatPanel';
import AgentPanel from "./components/AgentPanel";

export default function home(){
 return(
  <main className='h-screen flex flex-col bg-slate-950 text-white'>
    <Navbar/>
    <div className='flex flex-1 overflow-hidden'>

      <aside className="w-72 border-r border-slate-800"> 
          <Sidebar />
        </aside>

      <section className='flex-1'>
          <ChatPanel/>
      </section>

      <aside className='w-80 border-l border-slate-800'>
        <AgentPanel/>
      </aside>
      
    </div>



  </main>
 );
}
