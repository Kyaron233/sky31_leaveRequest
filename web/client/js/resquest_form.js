let addImageBtn = document.querySelector('.add_image')
let addImage = document.querySelector('.image_file')
let images = document.querySelector('.images')

// 为“添加图片”绑定点击事件
addImageBtn.addEventListener('click', e => {
  // 点击真正的添加文件按钮
  addImage.click()
})

// 创建 FormData 对象携带图片文件
let fd = new FormData()

// 获取 URL 对象
let windowURL = window.URL || window.webkitURL

// 定义函数进行base64编码
function fileToBase64(file, callback) {
  const reader = new FileReader()
  reader.onload = function (e) {
    // e.target.result 就是文件的 base64 编码
    callback(e.target.result)
  }
  // 读取文件并将其转换为 base64 编码
  reader.readAsDataURL(file)
}
let photos = []
// 监听选择图片
addImage.addEventListener('change', e => {
  // console.log(e.target.files)
  // 1. 获取图片文件
  let imgFileList = e.target.files
  // 未选择图片时直接退出程序
  if (imgFileList?.length < 1) return

  // 判断图片数量是否超过限制
  let oldImgs = document.querySelectorAll('.images img')
  if (imgFileList.length > 3 || imgFileList.length + oldImgs?.length > 3) {
    // 超过限制时阻止上传并弹出提示框
    popup.querySelector('.top').innerHTML = '添加失败！'
    popup.classList.remove('hide')
    return
  }
  Object.keys(imgFileList).forEach(key => {
    let imgFile = imgFileList[key]

    fileToBase64(imgFile, function (base64String) {
      console.log(base64String)
      // // 把图片存到内存中，并返回该图片的临时url
      // // 这里的url就是图片的内存地址
      // let url = windowURL.createObjectURL(new Blob([imgFile], { type: imgFile.type }))
      // // console.log(url)
      // 3. 创建一个新的 img 元素，并插入到 images 元素中
      let newImgEle = document.createElement('div')
      newImgEle.classList.add('image_ele')
      // newImgEle.innerHTML = `<span class="delete" --url="${url}" --name="${imgFile.name}">×</span><img src="${url}" alt="" />`
      newImgEle.innerHTML = `<span class="delete" --url="${base64String}">×</span><img src="${base64String}" alt="" />`

      images.insertBefore(newImgEle, addImageBtn)

      // 将图片存储到 FormData 对象中等待上传
      // fd.append(imgFile.name, imgFile)
      // console.log(fd.img)
      // console.log(fd)
      // 将图片存入数组
      photos.push(base64String)
    })
  })
  // 若已有三张图片则隐藏添加图片按钮
  if (document.querySelectorAll('.images img').length === 3) {
    addImageBtn.classList.add('hide')
  }

  popup.querySelector('.top').innerHTML = '添加成功！'
  popup.classList.remove('hide')
  // for (let [key, value] of fd.entries()) {
  //   console.log(key, value)
  // }
})

// 为页面绑定点击事件，用于点击“×”号时删除图片
document.addEventListener('click', e => {
  if (e.target.classList.contains('delete')) {
    // 删除页面元素
    e.target.parentElement.remove()
    photos.splice(photos.indexOf(e.target.getAttribute('--url')))
    // 删除 FormData 对象中的元素
    // fd.delete(e.target.getAttribute('--name'))
    // 清理内存
    // windowURL.revokeObjectURL(e.target.getAttribute('--url'))

    if (addImageBtn.classList.contains('hide')) {
      addImageBtn.classList.remove('hide')
    }
  }
  e.stopPropagation()
})

// 向服务器提交数据
let submitBtn = document.querySelector('.submit')
submitBtn.addEventListener('click', () => {
  // 获取表单数据
  let userData = {}
  let reason = document.querySelector('textarea').value
  userData.reason = reason
  console.log(reason)
  let id = location.href.split('=').splice(-1)[0]
  userData.event_id = id
  console.log(id)
  // 判断是否需要照片
  if (location.href.split('&')[0].split('=')[1] === 'true') {
    userData.photos = photos
  }

  console.log(userData)

  // 提交给服务器
  axios({
    method: 'post',
    url: `/main/leaveRequest`,
    data: userData
  })
    .then(result => {
      console.log(result)
      popup.querySelector('.top').innerHTML = '提交成功！'
      popup.classList.remove('hide')
    })
    .catch(error => {
      console.dir(error)
      // 登录失败，弹框提示
      popup.querySelector('.top').innerHTML = '提交申请失败！'
      popup.classList.remove('hide')
    })
})

// 点击返回事件
let backBtn = document.querySelector('.back')
backBtn.addEventListener('click', () => {
  // 跳转到上一页
  // location.href = location.href.split('#')[0]
  history.back()
})
