import express from "express";
import { getLocations, solveTsp } from "../controllers/tspController.js";

const router = express.Router();

router.get("/locations", getLocations);
router.post("/tsp/solve", solveTsp);

export default router;
