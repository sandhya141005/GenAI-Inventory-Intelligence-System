"use client";

import { useMemo, useState } from "react";
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  SortingState,
  useReactTable,
} from "@tanstack/react-table";
import { ArrowUpDown } from "lucide-react";
import { InventoryItem } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { formatCurrency } from "@/lib/utils";

const statusVariant: Record<InventoryItem["status"], "success" | "warning" | "danger" | "accent"> = {
  "in-stock": "success",
  "at-risk": "warning",
  stockout: "danger",
  overstock: "accent",
};

const healthLabel: Record<InventoryItem["health"], string> = {
  healthy: "Healthy",
  low: "Low",
  critical: "Critical",
  overstock: "Overstock",
};

export function InventoryTable({ data }: { data: InventoryItem[] }) {
  const [sorting, setSorting] = useState<SortingState>([]);

  const columns = useMemo<ColumnDef<InventoryItem>[]>(
    () => [
      { accessorKey: "sku", header: "SKU" },
      { accessorKey: "product", header: "Product" },
      { accessorKey: "store", header: "Store" },
      { accessorKey: "inventory", header: "Inventory" },
      { accessorKey: "demand", header: "Demand" },
      {
        accessorKey: "daysOfCover",
        header: "Days of Cover",
        cell: (info) => `${(info.getValue() as number).toFixed(1)}d`,
      },
      {
        accessorKey: "health",
        header: "Inventory Health",
        cell: (info) => (
          <Badge variant={statusVariant[info.row.original.status]}>
            {healthLabel[info.getValue() as InventoryItem["health"]]}
          </Badge>
        ),
      },
      {
        accessorKey: "revenueAtRisk",
        header: "Revenue at Risk",
        cell: (info) => {
          const value = info.getValue() as number;
          return value > 0 ? formatCurrency(value) : "—";
        },
      },
      {
        accessorKey: "status",
        header: "Status",
        cell: (info) => (
          <span className="capitalize text-xs text-ink-muted">
            {(info.getValue() as string).replace("-", " ")}
          </span>
        ),
      },
      {
        id: "actions",
        header: "Actions",
        cell: () => (
          <Button size="sm" variant="subtle">
            Inspect
          </Button>
        ),
      },
    ],
    []
  );

  const table = useReactTable({
    data,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  });

  return (
    <div className="overflow-x-auto rounded-lg border border-border bg-surface shadow-soft">
      <table className="w-full text-sm">
        <thead>
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id} className="border-b border-border">
              {headerGroup.headers.map((header) => (
                <th
                  key={header.id}
                  className="px-4 py-3 text-left text-xs font-medium text-ink-muted whitespace-nowrap select-none cursor-pointer"
                  onClick={header.column.getToggleSortingHandler()}
                >
                  <div className="flex items-center gap-1">
                    {flexRender(header.column.columnDef.header, header.getContext())}
                    {header.column.getCanSort() && (
                      <ArrowUpDown className="h-3 w-3" />
                    )}
                  </div>
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map((row) => (
            <tr
              key={row.id}
              className="border-b border-border last:border-0 hover:bg-gray-50/60 transition-colors cursor-pointer"
            >
              {row.getVisibleCells().map((cell) => (
                <td key={cell.id} className="px-4 py-3 whitespace-nowrap text-ink">
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
