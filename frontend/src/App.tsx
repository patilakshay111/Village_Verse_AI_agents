import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { Assets } from "./pages/Assets";
import { Businesses } from "./pages/Businesses";
import { CivilizationDashboard } from "./pages/CivilizationDashboard";
import { Dashboard } from "./pages/Dashboard";
import { Economy } from "./pages/Economy";
import { Families } from "./pages/Families";
import { FamilyDetail } from "./pages/FamilyDetail";
import { Locations } from "./pages/Locations";
import { Organizations } from "./pages/Organizations";
import { Search } from "./pages/Search";
import { Conversations } from "./pages/Conversations";
import { StoryFeed } from "./pages/StoryFeed";
import { VillagerDetail } from "./pages/VillagerDetail";
import { Villagers } from "./pages/Villagers";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="civilization" element={<CivilizationDashboard />} />
          <Route path="economy" element={<Economy />} />
          <Route path="assets" element={<Assets />} />
          <Route path="businesses" element={<Businesses />} />
          <Route path="organizations" element={<Organizations />} />
          <Route path="feed" element={<StoryFeed />} />
          <Route path="conversations" element={<Conversations />} />
          <Route path="villagers" element={<Villagers />} />
          <Route path="villagers/:id" element={<VillagerDetail />} />
          <Route path="families" element={<Families />} />
          <Route path="families/:id" element={<FamilyDetail />} />
          <Route path="locations" element={<Locations />} />
          <Route path="search" element={<Search />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
