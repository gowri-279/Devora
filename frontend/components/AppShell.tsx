import Sidebar from "./Sidebar";
import MobileHeader from "./MobileHeader";

export default function AppShell({ children }: { children: React.ReactNode }) {
  return <><Sidebar/><MobileHeader/><main className="min-h-screen md:ml-64"><div className="mx-auto max-w-7xl p-4 sm:p-6 lg:p-8">{children}</div></main></>;
}
