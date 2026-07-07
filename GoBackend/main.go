package main

import (
	"shazam-backend/src/routes"

	"github.com/gin-gonic/gin"
)

func main() {
	router := gin.Default()

	routes.FileRoutes(router)

	router.Run(":8080")
}