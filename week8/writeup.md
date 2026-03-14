# Week 8 Writeup: Automated UI and App Building

## Overview

This week covered AI-assisted frontend and full-stack application building — using tools like v0, Lovable, and Claude Artifacts to rapidly scaffold UIs, and then integrating them with backend APIs. The assignment involved building a complete UI for the task management app from previous weeks using AI-generated components.

---

## Part 1: AI UI Generation Tools

### Tool Comparison

| Tool | Strengths | Weaknesses |
|------|-----------|------------|
| **v0 (Vercel)** | React + Tailwind, production-quality components, excellent shadcn/ui integration | Requires Vercel ecosystem, limited backend integration |
| **Lovable** | Full-stack generation (React + Supabase), deploys in one click | Less control over code structure |
| **Claude Artifacts** | Flexible, great for self-contained widgets and prototypes | Stateless between sessions |
| **Cursor Composer** | Best for adding UI to an existing codebase | Requires existing project structure |

---

## Part 2: Building the Task Manager UI

### Step 1: Initial UI Generation with v0

**Prompt to v0:**
```
Create a task management dashboard with:
- A sidebar with navigation (Dashboard, Tasks, Analytics, Settings)
- A main content area showing a list of tasks in a card grid
- Each task card shows: title, status badge (Todo/In Progress/Done), due date, assignee avatar
- A "New Task" button that opens a modal form
- Filter controls at the top (by status, by date range)
- Dark mode support
Use shadcn/ui components and Tailwind CSS.
```

**Generated output:** A complete React component (~450 lines) with all requested features. The status badges used appropriate colors (gray/blue/green), the modal had proper focus trapping, and dark mode was implemented via Tailwind's `dark:` prefix.

**Iterations made:**
1. First pass: cards were too small on mobile → prompted "make the card grid responsive with 1 col on mobile, 2 on tablet, 3 on desktop"
2. Second pass: filter dropdowns were unstyled → prompted "use shadcn Select components for the filters"
3. Third pass: modal had no loading state → prompted "add a loading spinner to the submit button while the API call is in flight"

---

### Step 2: API Integration

After generating the static UI, I connected it to the FastAPI backend from previous weeks.

**Custom hook for data fetching:**
```typescript
// hooks/useTasks.ts
import { useState, useEffect } from "react";

interface Task {
  id: number;
  title: string;
  status: "todo" | "in_progress" | "done";
  due_date: string | null;
  assignee_id: number | null;
}

export function useTasks(filters: { status?: string; page?: number }) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    const params = new URLSearchParams();
    if (filters.status) params.set("status", filters.status);
    if (filters.page) params.set("page", String(filters.page));

    fetch(`/api/tasks?${params}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch tasks");
        return res.json();
      })
      .then((data) => {
        setTasks(data.tasks);
        setTotal(data.total);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [filters.status, filters.page]);

  return { tasks, loading, error, total };
}
```

**Prompt used to generate this hook:**
```
Generate a React custom hook called useTasks that fetches tasks from GET /api/tasks.
It should accept a filters object with optional status and page fields.
It should handle loading, error, and success states.
Auth token should be read from localStorage under the key "token".
Use TypeScript with proper types.
```

---

### Step 3: Auth Flow UI

**Prompt to Claude:**
```
Create a login/register page for a React app. Requirements:
- Two tabs: Login and Register
- Login: email + password fields, submit button
- Register: username, email, password, confirm password
- Show inline validation errors (password mismatch, empty fields)
- On successful login, store JWT from response in localStorage
- On success, redirect to /dashboard
- Use shadcn/ui form components
```

**Generated component (key parts):**
```tsx
// components/AuthPage.tsx
import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useNavigate } from "react-router-dom";

export function AuthPage() {
  const navigate = useNavigate();
  const [loginError, setLoginError] = useState("");
  const [registerErrors, setRegisterErrors] = useState<Record<string, string>>({});

  async function handleLogin(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        username: form.get("email") as string,
        password: form.get("password") as string,
      }),
    });
    if (!res.ok) {
      setLoginError("Invalid email or password");
      return;
    }
    const { access_token } = await res.json();
    localStorage.setItem("token", access_token);
    navigate("/dashboard");
  }

  // ... register handler with validation

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="w-full max-w-md space-y-8 rounded-xl bg-white p-8 shadow-lg dark:bg-gray-800">
        <h1 className="text-center text-2xl font-bold">Task Manager</h1>
        <Tabs defaultValue="login">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="login">Login</TabsTrigger>
            <TabsTrigger value="register">Register</TabsTrigger>
          </TabsList>
          {/* ... tab content */}
        </Tabs>
      </div>
    </div>
  );
}
```

---

### Step 4: Analytics Dashboard

**Prompt:**
```
Using recharts, create a dashboard with:
1. A line chart showing tasks created per day over the last 30 days
2. A pie chart showing task distribution by status (Todo, In Progress, Done)
3. A stat card row showing: Total Tasks, Completed This Week, Overdue Tasks
Data comes from GET /api/analytics which returns JSON.
```

**Generated output included:**
```tsx
import { LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

const STATUS_COLORS = {
  todo: "#94a3b8",
  in_progress: "#3b82f6",
  done: "#22c55e",
};

function AnalyticsDashboard({ data }) {
  return (
    <div className="space-y-6">
      {/* Stat cards */}
      <div className="grid grid-cols-3 gap-4">
        <StatCard label="Total Tasks" value={data.total} />
        <StatCard label="Completed This Week" value={data.completed_this_week} trend="+12%" />
        <StatCard label="Overdue" value={data.overdue} trend="-3%" trendPositive={false} />
      </div>

      {/* Line chart */}
      <div className="rounded-xl border bg-white p-6 dark:bg-gray-800">
        <h3 className="mb-4 font-semibold">Tasks Created (Last 30 Days)</h3>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={data.daily_counts}>
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Pie chart */}
      <div className="rounded-xl border bg-white p-6 dark:bg-gray-800">
        <h3 className="mb-4 font-semibold">Status Distribution</h3>
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie data={data.by_status} cx="50%" cy="50%" outerRadius={80} dataKey="count" nameKey="status">
              {data.by_status.map((entry) => (
                <Cell key={entry.status} fill={STATUS_COLORS[entry.status]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
```

---

## Part 3: Full Application Structure

The final application assembled from AI-generated components:

```
frontend/
├── src/
│   ├── components/
│   │   ├── AuthPage.tsx        # Login/Register (AI-generated)
│   │   ├── Dashboard.tsx       # Main layout + sidebar (AI-generated)
│   │   ├── TaskGrid.tsx        # Task card list with filters (AI-generated)
│   │   ├── TaskModal.tsx       # Create/edit task modal (AI-generated)
│   │   └── AnalyticsDashboard.tsx  # Charts + stats (AI-generated)
│   ├── hooks/
│   │   ├── useTasks.ts         # Data fetching hook (AI-generated)
│   │   └── useAuth.ts          # Auth state management (AI-generated)
│   └── App.tsx                 # Route definitions
```

**Time breakdown:**
- UI scaffolding (v0 + Claude): ~2 hours
- API integration and wiring: ~1.5 hours
- Testing and bug fixes: ~1 hour
- Total: ~4.5 hours for a complete full-stack UI

Manual estimate for the same UI without AI tools: ~20–30 hours.

---

## Reflections

1. **AI UI tools are genuinely production-ready for scaffolding.** The v0-generated components used correct accessibility attributes (`aria-label`, focus management in modals), responsive design, and dark mode — things I would often skip in a prototype.

2. **Iteration is the workflow.** No prompt produced a perfect result on the first try. The pattern of "generate → review → refine prompt → regenerate" is faster than writing from scratch but requires knowing what "good" looks like to spot what needs changing.

3. **Connecting AI-generated frontend to real backends requires human judgment.** The AI correctly generated the fetch calls but assumed the API response shape. When my actual API returned a slightly different structure, I had to manually reconcile the types. Always review the assumptions baked into generated code.

4. **Custom hooks are the cleanest integration point.** Generating a `useTasks` hook that encapsulates all the fetch logic meant the UI components stayed clean and the data-fetching logic was testable in isolation.

5. **The "developer as editor" role is real.** Across this entire project (weeks 1–8), the developer's role shifted from writing code to: specifying requirements, reviewing AI output, catching errors, and making architectural decisions. Writing code from scratch was a small fraction of total time by week 8.
