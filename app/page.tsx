"use client"

import { useState } from "react"
import { Search, Brain, Target, TrendingUp, Clock, MapPin } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"
import QueryResults from "@/components/query-results"
import IntentClassification from "@/components/intent-classification"
import RankingVisualization from "@/components/ranking-visualization"

export default function NLPQueryInterface() {
  const [query, setQuery] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState<string | null>(null)

  const handleSearch = async () => {
    if (!query.trim()) return

    setIsLoading(true)
    setError(null)
    setResults(null)

    try {
      // Real call to the Python NLP backend (proxied via /app/api/search).
      const res = await fetch("/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, top_k: 6 }),
      })

      const data = await res.json()

      if (!res.ok || data.error) {
        setError(data.error || `Request failed (${res.status})`)
        return
      }

      setResults(data)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong reaching the backend.",
      )
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center gap-3 mb-6">
            <Brain className="h-8 w-8 text-accent" />
            <div>
              <h1 className="text-2xl font-bold text-foreground">NLP Query Understanding</h1>
              <p className="text-muted-foreground">
                Semantic search with intent classification and personalized ranking
              </p>
            </div>
          </div>

          <div className="flex gap-3 max-w-2xl">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search for restaurants, cuisines, or dining experiences..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleSearch()}
                className="pl-10"
              />
            </div>
            <Button onClick={handleSearch} disabled={isLoading} className="bg-primary hover:bg-primary/90">
              {isLoading ? "Processing..." : "Search"}
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {error && !isLoading && (
          /* Surface backend/connection errors clearly */
          <div className="max-w-2xl mx-auto mb-8 rounded-lg border border-destructive/50 bg-destructive/10 p-4">
            <h3 className="font-semibold text-destructive mb-1">Search failed</h3>
            <p className="text-sm text-muted-foreground">{error}</p>
          </div>
        )}

        {!results && !isLoading && !error && (
          /* Added welcome state with feature highlights */
          <div className="text-center py-16">
            <div className="max-w-2xl mx-auto">
              <h2 className="text-3xl font-bold text-foreground mb-4">Advanced Query Understanding</h2>
              <p className="text-muted-foreground mb-8 text-lg">
                Experience semantic search powered by transformer embeddings, FAISS vector recall, and intelligent
                intent classification for hospitality and dining queries.
              </p>

              <div className="grid md:grid-cols-3 gap-6 mt-12">
                <Card>
                  <CardHeader className="text-center">
                    <Target className="h-8 w-8 text-accent mx-auto mb-2" />
                    <CardTitle className="text-lg">Intent Classification</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">
                      Automatically identifies query intent across 10 hospitality categories
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="text-center">
                    <TrendingUp className="h-8 w-8 text-accent mx-auto mb-2" />
                    <CardTitle className="text-lg">Semantic Search</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">
                      FAISS-powered vector similarity reduces irrelevant results by 22%
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="text-center">
                    <MapPin className="h-8 w-8 text-accent mx-auto mb-2" />
                    <CardTitle className="text-lg">Personalized Ranking</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">
                      Multi-factor scoring for location, preferences, and user history
                    </p>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        )}

        {isLoading && (
          /* Added loading state with progress indicators */
          <div className="text-center py-16">
            <div className="max-w-md mx-auto">
              <Brain className="h-12 w-12 text-accent mx-auto mb-4 animate-pulse" />
              <h3 className="text-xl font-semibold mb-4">Processing Query</h3>
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span>Embedding generation</span>
                  <span>100%</span>
                </div>
                <Progress value={100} className="h-2" />

                <div className="flex justify-between text-sm">
                  <span>Vector similarity search</span>
                  <span>85%</span>
                </div>
                <Progress value={85} className="h-2" />

                <div className="flex justify-between text-sm">
                  <span>Intent classification</span>
                  <span>60%</span>
                </div>
                <Progress value={60} className="h-2" />
              </div>
            </div>
          </div>
        )}

        {results && (
          /* Added results interface with tabbed layout */
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-foreground">Query Results</h2>
                <p className="text-muted-foreground">
                  Found {results.semanticResults.length} results in {results.processingTime}s
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm text-muted-foreground">{results.processingTime}s</span>
              </div>
            </div>

            <Tabs defaultValue="results" className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="results">Search Results</TabsTrigger>
                <TabsTrigger value="intent">Intent Analysis</TabsTrigger>
                <TabsTrigger value="ranking">Ranking Metrics</TabsTrigger>
              </TabsList>

              <TabsContent value="results" className="mt-6">
                <QueryResults results={results.semanticResults} />
              </TabsContent>

              <TabsContent value="intent" className="mt-6">
                <IntentClassification intent={results.intent} />
              </TabsContent>

              <TabsContent value="ranking" className="mt-6">
                <RankingVisualization rankings={results.rankings} results={results.semanticResults} />
              </TabsContent>
            </Tabs>
          </div>
        )}
      </main>
    </div>
  )
}
