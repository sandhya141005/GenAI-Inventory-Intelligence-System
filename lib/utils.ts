import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(value: number): string {
  if (Math.abs(value) >= 1_00_00_000) {
    return `INR ${(value / 1_00_00_000).toFixed(1)}Cr`;
  }
  if (Math.abs(value) >= 1_00_000) {
    return `INR ${(value / 1_00_000).toFixed(1)}L`;
  }
  return `INR ${value.toLocaleString("en-IN")}`;
}
