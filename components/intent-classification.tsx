import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Target, TrendingUp, Users } from "lucide-react"

interface Intent {
  primary: string
  confidence: number
  secondary: string[]
}

interface IntentClassificationProps {
  intent: Intent
}

const intentLabels: Record<string, { label: string; description: string; icon: any }> = {
  restaurant_search: {
    label: "Restaurant Search",
    description: "Looking for dining establishments",
    icon: Target,
  },
  cuisine_preference: {
    label: "Cuisine Preference",
    description: "Specific food type or style",
    icon: TrendingUp,
  },
  location_based: {
    label: "Location Based",
    description: "Geographic or proximity search",
    icon: Users,
  },
  reservation: {
    label: "Reservation",
    description: "Booking or availability inquiry",
    icon: Target,
  },
  dietary_restriction: {
    label: "Dietary Restriction",
    description: "Special dietary needs",
    icon: TrendingUp,
  },
}

export default function IntentClassification({ intent }: IntentClassificationProps) {
  const primaryIntent = intentLabels[intent.primary]
  const IconComponent = primaryIntent?.icon || Target

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <IconComponent className="h-5 w-5 text-accent" />
            Primary Intent Classification
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-xl font-semibold">{primaryIntent?.label || intent.primary}</h3>
              <p className="text-muted-foreground">{primaryIntent?.description}</p>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-accent">{(intent.confidence * 100).toFixed(1)}%</div>
              <div className="text-sm text-muted-foreground">Confidence</div>
            </div>
          </div>
          <Progress value={intent.confidence * 100} className="h-3" />
        </CardContent>
      </Card>

      <div>
        <h3 className="text-lg font-semibold mb-4">Secondary Intent Signals</h3>
        <div className="grid md:grid-cols-2 gap-4">
          {intent.secondary.map((secondaryIntent, index) => {
            const intentInfo = intentLabels[secondaryIntent]
            const SecondaryIcon = intentInfo?.icon || Target
            // Simulate confidence scores for secondary intents
            const confidence = 0.8 - index * 0.1

            return (
              <Card key={secondaryIntent}>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-3 mb-3">
                    <SecondaryIcon className="h-4 w-4 text-muted-foreground" />
                    <div className="flex-1">
                      <h4 className="font-medium">{intentInfo?.label || secondaryIntent}</h4>
                      <p className="text-sm text-muted-foreground">{intentInfo?.description}</p>
                    </div>
                    <Badge variant="outline">{(confidence * 100).toFixed(0)}%</Badge>
                  </div>
                  <Progress value={confidence * 100} className="h-2" />
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Classification Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-foreground">10</div>
              <div className="text-sm text-muted-foreground">Intent Categories</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-foreground">94.2%</div>
              <div className="text-sm text-muted-foreground">Avg Accuracy</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-foreground">0.12s</div>
              <div className="text-sm text-muted-foreground">Classification Time</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-foreground">22%</div>
              <div className="text-sm text-muted-foreground">Relevance Improvement</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
