package routes

import (
	"shazam-backend/src/controllers"

	"github.com/gin-gonic/gin"
)

func FileRoutes(router *gin.Engine) {
	router.POST("/shazam/uploadfile", controllers.UploadFileController)
}