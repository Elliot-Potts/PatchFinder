import { useState } from "react"
import { ConnectionForm } from "@/components/ConnectionForm"
import { useToast } from "@/hooks/use-toast"
import { Toaster } from "@/components/ui/toaster"

function App() {
  const [isLoading, setIsLoading] = useState(false)
  const { toast } = useToast()

  const handleConnect = async (data: { ip: string; username: string; password: string }) => {
    setIsLoading(true)
    try {
      const response = await fetch("http://localhost:8000/api/connect", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`)
      }

      const result = await response.json()
      console.log(result) // We'll handle the results display next
      toast({
        title: "Connected successfully",
        description: `Connected to ${result.hostname}`,
      })
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Connection failed",
        description: error instanceof Error ? error.message : "Unknown error occurred",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <>
      <div className="min-h-screen bg-background p-8">
        <div className="container mx-auto max-w-2xl">
          <h1 className="text-4xl font-bold mb-8">PatchFinder</h1>
          <ConnectionForm onConnect={handleConnect} isLoading={isLoading} />
        </div>
      </div>
      <Toaster />
    </>
  )
}

export default App
