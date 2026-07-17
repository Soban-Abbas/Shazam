package main

import (
	"time"
	"shazam-backend/src/routes"

	"github.com/gin-gonic/gin"


 "github.com/gin-contrib/cors"


)

func main() {
	router := gin.Default()

	router.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"*"},
		AllowMethods:     []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Authorization"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: false,
		MaxAge:           12 * time.Hour,
	}))

	routes.FileRoutes(router)

	router.Run(":8080")
}