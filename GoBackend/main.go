package main

import (
	"shazam-backend/src/routes"

	"github.com/gin-gonic/gin"


 "github.com/gin-contrib/cors"


)

func main() {
	router := gin.Default()
router.Use(cors.Default())
	routes.FileRoutes(router)

	router.Run(":8080")
}