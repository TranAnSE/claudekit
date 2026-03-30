# shadcn/ui Component Recipes

Common compositions using shadcn/ui. Install components via `npx shadcn@latest add`.

---

## Search Command Palette

```bash
npx shadcn@latest add command dialog
```

```tsx
import { useState, useEffect } from "react";
import {
  CommandDialog, CommandEmpty, CommandGroup,
  CommandInput, CommandItem, CommandList,
} from "@/components/ui/command";

const items = [
  { group: "Pages", entries: [
    { label: "Dashboard", href: "/dashboard" },
    { label: "Settings", href: "/settings" },
  ]},
  { group: "Actions", entries: [
    { label: "Create project", action: "new-project" },
  ]},
];

export function CommandPalette() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((prev) => !prev);
      }
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, []);

  return (
    <CommandDialog open={open} onOpenChange={setOpen}>
      <CommandInput placeholder="Type a command or search..." />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>
        {items.map((group) => (
          <CommandGroup key={group.group} heading={group.group}>
            {group.entries.map((entry) => (
              <CommandItem key={entry.label} onSelect={() => setOpen(false)}>
                {entry.label}
              </CommandItem>
            ))}
          </CommandGroup>
        ))}
      </CommandList>
    </CommandDialog>
  );
}
```

---

## Settings Form

`npx shadcn@latest add form input switch button separator`

```tsx
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";

const schema = z.object({ displayName: z.string().min(2).max(50), email: z.string().email(), notifications: z.boolean() });

export function SettingsForm() {
  const form = useForm<z.infer<typeof schema>>({
    resolver: zodResolver(schema),
    defaultValues: { displayName: "", email: "", notifications: true },
  });
  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h2 className="text-lg font-semibold">Settings</h2>
        <p className="text-sm text-muted-foreground">Manage your account preferences.</p>
      </div>
      <Separator />
      <Form {...form}>
        <form onSubmit={form.handleSubmit(console.log)} className="space-y-6">
          <FormField control={form.control} name="displayName" render={({ field }) => (
            <FormItem><FormLabel>Display Name</FormLabel><FormControl><Input placeholder="Jane Doe" {...field} /></FormControl><FormMessage /></FormItem>
          )} />
          <FormField control={form.control} name="email" render={({ field }) => (
            <FormItem><FormLabel>Email</FormLabel><FormControl><Input type="email" {...field} /></FormControl><FormMessage /></FormItem>
          )} />
          <FormField control={form.control} name="notifications" render={({ field }) => (
            <FormItem className="flex items-center justify-between rounded-lg border p-4">
              <div><FormLabel>Notifications</FormLabel><FormDescription>Receive account emails.</FormDescription></div>
              <FormControl><Switch checked={field.value} onCheckedChange={field.onChange} /></FormControl>
            </FormItem>
          )} />
          <Button type="submit">Save changes</Button>
        </form>
      </Form>
    </div>
  );
}
```

---

## Data Table with Filters

`npx shadcn@latest add table input button badge dropdown-menu`

```tsx
import { useState, useMemo } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";

interface User { id: string; name: string; email: string; role: "admin" | "user"; status: "active" | "inactive"; }

export function UsersTable({ users }: { users: User[] }) {
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState<string | null>(null);
  const filtered = useMemo(() => users.filter((u) => {
    const match = u.name.toLowerCase().includes(search.toLowerCase()) || u.email.toLowerCase().includes(search.toLowerCase());
    return match && (!roleFilter || u.role === roleFilter);
  }), [users, search, roleFilter]);

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <Input placeholder="Search..." value={search} onChange={(e) => setSearch(e.target.value)} className="max-w-sm" />
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm">{roleFilter ?? "All roles"}</Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuItem onClick={() => setRoleFilter(null)}>All</DropdownMenuItem>
            <DropdownMenuItem onClick={() => setRoleFilter("admin")}>Admin</DropdownMenuItem>
            <DropdownMenuItem onClick={() => setRoleFilter("user")}>User</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
      <Table>
        <TableHeader><TableRow>
          <TableHead>Name</TableHead><TableHead>Email</TableHead><TableHead>Role</TableHead><TableHead>Status</TableHead>
        </TableRow></TableHeader>
        <TableBody>{filtered.map((u) => (
          <TableRow key={u.id}>
            <TableCell className="font-medium">{u.name}</TableCell>
            <TableCell>{u.email}</TableCell>
            <TableCell><Badge variant={u.role === "admin" ? "default" : "secondary"}>{u.role}</Badge></TableCell>
            <TableCell><Badge variant={u.status === "active" ? "default" : "outline"}>{u.status}</Badge></TableCell>
          </TableRow>
        ))}</TableBody>
      </Table>
    </div>
  );
}
```

---

## Dashboard Layout with Sidebar

`npx shadcn@latest add button separator sheet avatar`

```tsx
import { ReactNode } from "react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";

const navItems = [
  { label: "Dashboard", href: "/", active: true },
  { label: "Projects", href: "/projects" },
  { label: "Settings", href: "/settings" },
];

function SidebarNav() {
  return (
    <div className="flex h-full flex-col">
      <div className="px-4 py-5 text-lg font-bold">App Name</div>
      <Separator />
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navItems.map((item) => (
          <a key={item.href} href={item.href} className={`block rounded-md px-3 py-2 text-sm font-medium ${
            item.active ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-muted"}`}>
            {item.label}
          </a>
        ))}
      </nav>
      <Separator />
      <div className="flex items-center gap-3 px-4 py-4">
        <Avatar className="h-8 w-8"><AvatarImage src="/avatar.jpg" /><AvatarFallback>JD</AvatarFallback></Avatar>
        <div className="truncate">
          <p className="text-sm font-medium">Jane Doe</p>
          <p className="text-xs text-muted-foreground">jane@example.com</p>
        </div>
      </div>
    </div>
  );
}

export function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex h-screen">
      <aside className="hidden w-64 border-r bg-card lg:block"><SidebarNav /></aside>
      <div className="flex flex-1 flex-col">
        <header className="flex h-14 items-center gap-4 border-b px-4 lg:hidden">
          <Sheet>
            <SheetTrigger asChild><Button variant="ghost" size="icon">Menu</Button></SheetTrigger>
            <SheetContent side="left" className="w-64 p-0"><SidebarNav /></SheetContent>
          </Sheet>
        </header>
        <main className="flex-1 overflow-y-auto p-6 lg:p-8">{children}</main>
      </div>
    </div>
  );
}
```

---

## Tips

- Use `cn()` from `@/lib/utils` to merge conditional classes
- Pair with `react-hook-form` + `zod` for form validation
- Use `Sheet` for mobile sidebars, `Dialog` for modals
- Customize theme in `globals.css` using CSS variables
