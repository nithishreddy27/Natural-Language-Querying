import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from "recharts"

interface RankingVisualizationProps {
  rankings: {
    semantic: number[]
    intent: number[]
    personalized: number[]
    location: number[]
  }
  results: Array<{ name: string }>
}

export default function RankingVisualization({ rankings, results }: RankingVisualizationProps) {
  // Prepare data for bar chart
  const barData = results.map((result, index) => ({
    name: result.name.split(" ")[0], // Shortened name for chart
    semantic: rankings.semantic[index] * 100,
    intent: rankings.intent[index] * 100,
    personalized: rankings.personalized[index] * 100,
    location: rankings.location[index] * 100,
  }))

  // Prepare data for radar chart (average scores)
  const radarData = [
    {
      factor: "Semantic Similarity",
      score: (rankings.semantic.reduce((a, b) => a + b, 0) / rankings.semantic.length) * 100,
    },
    {
      factor: "Intent Matching",
      score: (rankings.intent.reduce((a, b) => a + b, 0) / rankings.intent.length) * 100,
    },
    {
      factor: "Personalization",
      score: (rankings.personalized.reduce((a, b) => a + b, 0) / rankings.personalized.length) * 100,
    },
    {
      factor: "Location Proximity",
      score: (rankings.location.reduce((a, b) => a + b, 0) / rankings.location.length) * 100,
    },
  ]

  return (
    <div className="space-y-6">
      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Ranking Factor Comparison</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={barData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="semantic" fill="hsl(var(--chart-1))" name="Semantic" />
                <Bar dataKey="intent" fill="hsl(var(--chart-2))" name="Intent" />
                <Bar dataKey="personalized" fill="hsl(var(--chart-3))" name="Personalized" />
                <Bar dataKey="location" fill="hsl(var(--chart-4))" name="Location" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Average Factor Performance</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="factor" />
                <PolarRadiusAxis angle={90} domain={[0, 100]} />
                <Radar
                  name="Score"
                  dataKey="score"
                  stroke="hsl(var(--accent))"
                  fill="hsl(var(--accent))"
                  fillOpacity={0.3}
                />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4">
        <h3 className="text-lg font-semibold">Detailed Ranking Breakdown</h3>
        {results.map((result, index) => (
          <Card key={index}>
            <CardHeader>
              <CardTitle className="text-base">{result.name}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Semantic Similarity</span>
                      <span>{(rankings.semantic[index] * 100).toFixed(1)}%</span>
                    </div>
                    <Progress value={rankings.semantic[index] * 100} className="h-2" />
                  </div>

                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Intent Matching</span>
                      <span>{(rankings.intent[index] * 100).toFixed(1)}%</span>
                    </div>
                    <Progress value={rankings.intent[index] * 100} className="h-2" />
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Personalized Score</span>
                      <span>{(rankings.personalized[index] * 100).toFixed(1)}%</span>
                    </div>
                    <Progress value={rankings.personalized[index] * 100} className="h-2" />
                  </div>

                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Location Proximity</span>
                      <span>{(rankings.location[index] * 100).toFixed(1)}%</span>
                    </div>
                    <Progress value={rankings.location[index] * 100} className="h-2" />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Ranking Pipeline Performance</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-accent">4</div>
              <div className="text-sm text-muted-foreground">Ranking Factors</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-accent">22%</div>
              <div className="text-sm text-muted-foreground">Relevance Boost</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-accent">0.08s</div>
              <div className="text-sm text-muted-foreground">Ranking Time</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-accent">96.4%</div>
              <div className="text-sm text-muted-foreground">User Satisfaction</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
