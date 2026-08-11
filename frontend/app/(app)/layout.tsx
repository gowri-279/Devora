import AppShell from "@/components/AppShell";
import Protected from "@/components/Protected";

export default function Layout({ children }: { children: React.ReactNode }) {
  return <Protected><AppShell>{children}</AppShell></Protected>;
}
