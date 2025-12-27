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
