"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import { useState, useEffect } from "react";
import { hoverButton, hoverSubtle } from "@/lib/motion";

export default function Navbar() {
  const pathname = usePathname();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const navLink = (href: string, label: string) => {
    const isActive = pathname === href;
    return (
      <Link
        href={href}
        className={`relative text-sm font-medium transition-colors duration-200 ${
          isActive ? "text-content-primary" : "text-content-secondary hover:text-content-primary"
        }`}
      >
        {label}
        {isActive && (
          <motion.div
            layoutId="navbar-indicator"
            className="absolute -bottom-1 left-0 right-0 h-0.5 bg-brand"
            transition={{ type: "spring", stiffness: 380, damping: 30 }}
          />
        )}
      </Link>
    );
  };

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ type: "spring", stiffness: 100, damping: 20 }}
      className={`sticky top-0 z-50 border-b transition-all duration-300 ${
        scrolled
          ? "border-border-default/80 bg-surface-primary/85 backdrop-blur-xl shadow-lg"
          : "border-border-subtle/60 bg-surface-primary/60 backdrop-blur-sm"
      }`}
    >
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        {/* Logo */}
        <Link href="/" className="group flex items-center gap-3">
          <motion.div
            {...hoverSubtle}
            transition={{ type: "spring", stiffness: 400, damping: 17 }}
          >
            <Image
              src="/logo-main.png"
              alt="AccessLens"
              width={40}
              height={40}
              className="rounded-lg"
              onError={(e) => {
                (e.target as HTMLImageElement).style.display = "none";
              }}
            />
          </motion.div>
          <div className="flex flex-col">
            <span className="text-lg font-bold text-content-primary">
              AccessLens{" "}
              <span className="text-brand-soft">v2</span>
            </span>
            <span className="text-xs text-content-muted">Policy Access Engine</span>
          </div>
        </Link>

        {/* Nav links */}
        <div className="flex items-center gap-8">
          {navLink("/", "Home")}
          <motion.div {...hoverButton}>
            <Link href="/input" className="btn btn-primary text-sm">
              Get Started
            </Link>
          </motion.div>
        </div>
      </div>
    </motion.nav>
  );
}
