// Signal Garden style reminder: keep the global shell dark and calm; Bob belongs at the app root so it persists across every route/view.
import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import Home from "./pages/Home";

export default function App() {
  return <ErrorBoundary><ThemeProvider defaultTheme="dark"><TooltipProvider><Toaster theme="dark" /><Home /></TooltipProvider></ThemeProvider></ErrorBoundary>;
}
