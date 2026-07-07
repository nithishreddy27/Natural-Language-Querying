import { Card, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Star, MapPin, DollarSign } from "lucide-react"
import { Progress } from "@/components/ui/progress"

interface QueryResult {
  id: number
  name: string
  description: string
  similarity: number
  category: string
  location: string
  rating: number
  price: string
}

interface QueryResultsProps {
  results: QueryResult[]
}

export default function QueryResults({ results }: QueryResultsProps) {
  return (
    <div className="space-y-4">
      {results.map((result, index) => (
        <Card key={result.id} className="hover:shadow-md transition-shadow">
          <CardHeader>
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <CardTitle className="text-lg">{result.name}</CardTitle>
                  <Badge variant="secondary" className="text-xs">
                    Rank #{index + 1}
                  </Badge>
                </div>
                <p className="text-muted-foreground text-sm mb-3">{result.description}</p>

                <div className="flex items-center gap-4 text-sm">
                  <div className="flex items-center gap-1">
                    <Star className="h-4 w-4 text-yellow-500 fill-current" />
                    <span>{result.rating}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <MapPin className="h-4 w-4 text-muted-foreground" />
                    <span>{result.location}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <DollarSign className="h-4 w-4 text-muted-foreground" />
                    <span>{result.price}</span>
                  </div>
                  <Badge variant="outline">{result.category}</Badge>
                </div>
              </div>

              <div className="text-right ml-4">
                <div className="text-sm font-medium text-muted-foreground mb-1">Similarity Score</div>
                <div className="text-2xl font-bold text-accent">{(result.similarity * 100).toFixed(1)}%</div>
                <Progress value={result.similarity * 100} className="w-20 h-2 mt-2" />
              </div>
            </div>
          </CardHeader>
        </Card>
      ))}
    </div>
  )
}
