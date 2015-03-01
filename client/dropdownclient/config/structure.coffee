# Read more about app structure at http://docs.appgyver.com

module.exports =
  initialView:
    id: "initialView"
    location: "http://localhost/login.html"
    navigationBar: false

  rootView:
    location: "http://localhost/index.html"
    navigationBar: false
    id: "rootView"

  preloads: [
    {
      id: "upload-avatar"
      location: "http://localhost/upload_avatar.html"
    }
  ]
