import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, Link, RouterProvider } from "react-router";
import { AppLayout } from "./components/Layout";
import "./index.css";
import EditorVacante from "./pages/EditorVacante";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Panel from "./pages/Panel";
import Ranking from "./pages/Ranking";
import SubirCVs from "./pages/SubirCVs";
import Vacantes from "./pages/Vacantes";

const NoEncontrada = () => (
  <div className="flex min-h-dvh flex-col items-center justify-center gap-3 text-center">
    <p className="text-sm text-zinc-500">Esta página no existe.</p>
    <Link to="/app" className="btn-primario">Ir al panel</Link>
  </div>
);

const router = createBrowserRouter([
  { path: "/", element: <Landing /> },
  { path: "/login", element: <Login /> },
  {
    path: "/app",
    element: <AppLayout />,
    children: [
      { index: true, element: <Panel /> },
      { path: "vacantes", element: <Vacantes /> },
      { path: "vacantes/nueva", element: <EditorVacante /> },
      { path: "vacantes/:id", element: <EditorVacante /> },
      { path: "vacantes/:id/cvs", element: <SubirCVs /> },
      { path: "vacantes/:id/ranking", element: <Ranking /> },
    ],
  },
  { path: "*", element: <NoEncontrada /> },
]);

const qc = new QueryClient({ defaultOptions: { queries: { staleTime: 5000, refetchOnWindowFocus: false, retry: 1 } } });

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={qc}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </StrictMode>,
);
