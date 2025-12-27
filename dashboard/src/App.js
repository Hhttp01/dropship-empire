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
