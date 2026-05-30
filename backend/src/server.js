import cors from "cors";
import express from "express";
import tspRoutes from "./routes/tspRoutes.js";

const app = express();
const PORT = 5000;

app.use(cors());
app.use(express.json());

app.get("/", (req, res) => {
  res.json({
    success: true,
    message: "TSP Dynamic Programming Route Optimizer API berjalan."
  });
});

app.use("/api", tspRoutes);

app.use((req, res) => {
  res.status(404).json({ success: false, message: "Endpoint tidak ditemukan." });
});

app.listen(PORT, () => {
  console.log(`Backend berjalan di http://localhost:${PORT}`);
});
