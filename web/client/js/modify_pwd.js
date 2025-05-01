// 修改密码
// 限制输入框输入不可为汉字
let inputs = document.querySelector('.pwd')
inputs.addEventListener('input', e => {
  let inputEle = e.target
  inputEle.value = inputEle.value.replace(/[\u4E00-\u9FA5]/g, '')
})

// 点击按钮提交到服务器

let submitBtn = document.querySelector('.submit')
submitBtn.addEventListener('click', e => {
  // 获取输入框中的新旧密码
  let old_pswd = inputs.querySelector('.old_pswd').value
  let new_pswd = inputs.querySelector('.new_pswd').value
  if (!old_pswd || !new_pswd) {
    popupTop.innerHTML = '保存失败！'
    popup.classList.remove('hide')
    return
  }
  // 向服务器提交数据
  axios({
    method: 'post',
    url: '/update_pswd',
    data: {
      old_pswd,
      new_pswd
    }
  })
    .then(result => {
      console.log(result)
      popupTop.innerHTML = '保存成功！'
      popup.classList.remove('hide')
    })
    .catch(error => {
      console.dir(error)
      popupTop.innerHTML = '保存失败！'
      popup.classList.remove('hide')
    })
  // 跳转到主页
})
