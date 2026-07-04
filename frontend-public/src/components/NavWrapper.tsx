"use client";

import { usePathname } from "next/navigation";
import AlertBanner from "./AlertBanner";
import Navbar from "./Navbar";

export default function NavWrapper() {
  const pathname = usePathname();
  if (pathname.includes("/auth/")) return null;
  return (
    <>
      <AlertBanner />
      <Navbar />
    </>
  );
}
