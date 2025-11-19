import { Button } from "@/components/ui/button";

export default function DashboardPage() {
    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
                <div className="flex items-center gap-2">
                    <Button variant="outline">Download Report</Button>
                    <Button>Add Meal</Button>
                </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                {/* Placeholder Stats Cards */}
                {["Calories", "Protein", "Carbs", "Fat"].map((item) => (
                    <div key={item} className="rounded-xl border bg-card text-card-foreground shadow p-6">
                        <div className="text-sm font-medium text-muted-foreground">{item}</div>
                        <div className="text-2xl font-bold mt-2">--</div>
                    </div>
                ))}
            </div>
        </div>
    );
}
