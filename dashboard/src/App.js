// הוספת החיבור ל-Backend
const [products, setProducts] = useState([]);

useEffect(() => {
  const syncData = async () => {
    const response = await fetch('http://localhost:8000/api/inventory'); // פונה ל-Backend
    const data = await response.json();
    setProducts(data);
  };
  syncData();
}, []);
import React, { useState, useEffect } from 'react';
import { Search, ShoppingCart, CheckCircle, Trash2, Cpu, Home, Package, Zap, Loader2, Camera } from 'lucide-react';

const App = () => {
  const [activeTab, setActiveTab] = useState('home'); 
  const [inventory, setInventory] = useState([]);
  const [actions, setActions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [niche, setNiche] = useState("");

  // --- פונקציות תקשורת עם ה-Backend ---
  const fetchData = async () => {
    const [invRes, actRes] = await Promise.all([
      fetch('http://localhost:8000/api/inventory'),
      fetch('http://localhost:8000/api/actions')
    ]);
    setInventory(await invRes.json());
    setActions(await actRes.json());
  };

  useEffect(() => { fetchData(); }, []);

  const startScan = async () => {
    if (!niche) return;
    setLoading(true);
    await fetch(`http://localhost:8000/api/run?niche=${niche}`, { method: 'POST' });
    setNiche("");
    await fetchData();
    setLoading(false);
  };

  const deleteProduct = async (id) => {
    await fetch(`http://localhost:8000/api/delete/${id}`, { method: 'DELETE' });
    fetchData();
  };

  return (
    <div className="min-h-screen bg-[#020617] text-white p-4 md:p-8 font-sans" dir="rtl">
      {/* Header */}
      <header className="max-w-7xl mx-auto mb-8 bg-white/5 p-6 rounded-[28px] border border-white/10 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="bg-indigo-500 p-2 rounded-lg"><Cpu size={24} /></div>
          <h1 className="text-2xl font-black italic">EMPIRE<span className="text-indigo-400">OS</span></h1>
        </div>
        <div className="flex gap-4">
          <button onClick={() => setActiveTab('home')} className={`p-2 rounded-xl ${activeTab === 'home' ? 'bg-indigo-500' : 'bg-white/5'}`}><Home /></button>
          <button onClick={() => setActiveTab('inventory')} className={`p-2 rounded-xl ${activeTab === 'inventory' ? 'bg-indigo-500' : 'bg-white/5'}`}><Package /></button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* תוכן משתנה לפי דפים */}
        <div className="lg:col-span-8 space-y-6">
          {activeTab === 'home' && (
            <section className="bg-white/5 p-8 rounded-[32px] border border-white/10">
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2"><Search className="text-indigo-400" /> סריקת נישה חדשה</h2>
              <div className="flex gap-4">
                <input 
                  value={niche} 
                  onChange={(e) => setNiche(e.target.value)}
                  placeholder="הכנס שם מוצר או נישה..." 
                  className="flex-1 bg-black/40 border border-white/10 p-4 rounded-2xl outline-none focus:border-indigo-500 transition-all"
                />
                <button onClick={startScan} disabled={loading} className="bg-indigo-500 px-8 rounded-2xl font-bold hover:scale-105 active:scale-95 transition-all">
                  {loading ? <Loader2 className="animate-spin" /> : "סרוק עכשיו"}
                </button>
              </div>
            </section>
          )}

          {(activeTab === 'home' || activeTab === 'inventory') && (
            <section className="bg-white/5 p-6 rounded-[32px] border border-white/10">
              <h2 className="text-xl font-bold mb-6">נכסים באחסון ({inventory.length})</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {inventory.map(item => (
                  <div key={item.id} className="bg-black/20 p-4 rounded-2xl border border-white/5 flex gap-4 relative group">
                    <div className="w-20 h-20 bg-white/5 rounded-xl overflow-hidden">
                      {item.image_path ? <img src={`http://localhost:8000${item.image_path}`} alt="AI" className="w-full h-full object-cover" /> : <div className="p-6 text-white/20"><Camera /></div>}
                    </div>
                    <div className="flex-1">
                      <p className="font-bold text-indigo-100">{item.title}</p>
                      <p className="text-xs text-white/40">רווח פוטנציאלי: <span className="text-green-400">${item.profit}</span></p>
                      <div className="mt-2 flex gap-2">
                        {item.is_golden === 1 && <span className="text-[10px] bg-yellow-500/20 text-yellow-500 px-2 py-1 rounded-full border border-yellow-500/20">מוצר זהב</span>}
                      </div>
                    </div>
                    <button onClick={() => deleteProduct(item.id)} className="absolute top-4 left-4 text-white/20 hover:text-red-400 transition-colors"><Trash2 size={16}/></button>
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>

        {/* Sidebar: אישורים (מכל הקודים הקודמים) */}
        <div className="lg:col-span-4 space-y-6">
          <section className="bg-indigo-500/10 p-6 rounded-[32px] border border-indigo-500/20">
            <h2 className="text-lg font-black flex items-center gap-2 mb-4"><Zap className="text-orange-400" /> פעולות AI לאישור</h2>
            <div className="space-y-3">
              {actions.length === 0 && <p className="text-xs text-white/20">אין פעולות ממתינות...</p>}
              {actions.map(action => (
                <div key={action.id} className="bg-black/40 p-4 rounded-2xl border border-white/5">
                  <p className="text-sm font-bold">{action.title}</p>
                  <p className="text-[11px] text-white/40 mb-3">{action.desc}</p>
                  <button className="w-full bg-indigo-500 text-xs py-2 rounded-xl font-bold">אשר פעולה</button>
                </div>
              ))}
            </div>
          </section>
        </div>
      </main>
    </div>
  );
};

export default App;
