const API_BASE_URL = 'http://localhost:8000/api/v1';

export const EmpireAPI = {
  // שליפת כל המלאי מה-DB
  getInventory: async () => {
    const response = await fetch(`${API_BASE_URL}/inventory`);
    return await response.json();
  },

  // שליפת הפעולות שממתינות לאישור (ADS, TikTok וכו')
  getPendingActions: async () => {
    const response = await fetch(`${API_BASE_URL}/actions`);
    return await response.json();
  },

  // פונקציה להפעלת סריקה חדשה מהממשק
  runScan: async (niche) => {
    const response = await fetch(`${API_BASE_URL}/run?niche=${niche}`, { method: 'POST' });
    return await response.json();
  }
};
import { EmpireAPI } from './services/api';

const App = () => {
  const [inventory, setInventory] = useState([]);
  const [pendingActions, setPendingActions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // פונקציה לטעינת כל הנתונים מהשרת
  const refreshData = async () => {
    try {
      const [invData, actionsData] = await Promise.all([
        EmpireAPI.getInventory(),
        EmpireAPI.getPendingActions()
      ]);
      setInventory(invData);
      setPendingActions(actionsData);
      setIsLoading(false);
    } catch (error) {
      console.error("Connection to EmpireOS Backend failed");
    }
  };

  useEffect(() => {
    refreshData();
    // שדרוג 1: רענון אוטומטי כל 30 שניות
    const interval = setInterval(refreshData, 30000);
    return () => clearInterval(interval);
  }, []);

  // ... כאן מגיע ה-return עם ה-HTML/Tailwind שלך ...
};
