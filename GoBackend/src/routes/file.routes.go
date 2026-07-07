package routes

import (
	"shazam-backend/src/controllers"

	"github.com/gin-gonic/gin"
	"shazam-backend/src/middlewares"
)

func FileRoutes(router *gin.Engine) {
		router.POST("/shazam/login", controllers.LoginController) 
	router.POST("/shazam/uploadfile", controllers.UploadFileController)
	router.POST("/shazam/addsong",middlewares.AuthMiddleware(), controllers.AddSongController)
}