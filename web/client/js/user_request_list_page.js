// 绑定活动的修改和删除操作
// 修改
let modifyBtn = document.querySelector('.right .modify')
modifyBtn.addEventListener('click', () => {
  // 跳转到活动编辑页面（发布活动页面）
  // 获取活动id
  let eventID = location.href.split('=')[1]
  // 渲染信息
  document.querySelector('input[name="event_name"]').value = activityName.innerHTML
  document.querySelector('.activity_type.type span').innerHTML = activityType.innerHTML
  document.querySelector('input[name="event_type"]').value = activityType.innerHTML
  let dates = expirationDate.innerHTML.split('.')
  document.querySelector('.year span').innerHTML = dates[0]
  document.querySelector('.month span').innerHTML = dates[1] > 9 ? dates[1] : dates[1].slice(-1)
  document.querySelector('.day span').innerHTML = dates[2] > 9 > 1 ? dates[2] : dates[2].slice(-1)
  document.querySelector('.hour span').innerHTML = 0
  proveStatus.innerHTML === '是' ? document.querySelector('#option1').click() : document.querySelector('#option2').click()
  // 修改 URL
  location.href = location.href.split('#')[0] + `#modifyActivity?event_id=${eventID}`
  // 页面切换
  // showPage(issueNewActivityPage)
})

// 删除
let deleteBtn = document.querySelector('.right .delete')

deleteBtn.addEventListener('click', () => {
  // 确认删除
  popupTop.innerHTML = '确认删除！'
  popup.classList.remove('hide')
  // if (1) {
  //   // 执行删除操作
  //   //...
  // } else {
  //   // 取消删除
  //   return
  // }
  // // 关闭窗口
})

// 获取请假表数据
let whoName = document.querySelector('.user_form .name input')
let whoStuId = document.querySelector('.user_form .stu_id input')
let whoReason = document.querySelector('.user_form .reason textarea')
let whoPhotos = document.querySelector('.user_form .images')
function getData(id) {
  whoName.value = ''
  whoStuId.value = ''
  whoReason.value = ''
  whoPhotos.innerHTML = ''
  axios({
    method: 'get',
    url: `/main/leaveRequest/${id}`
  })
    .then(result => {
      console.log(result.data)
      if (result.data.message) return
      let data = result.data
      console.log(data)
      whoName.value = data.whoLeave_name
      whoStuId.value = data.whoLeave_id
      whoReason.value = data.whoLeave_reason
      Object.keys(data.whoLeave_photo).forEach(base64String => {
        let newImgEle = document.createElement('div')
        newImgEle.classList.add('image_ele')
        newImgEle.innerHTML = `<span class="delete" --url="${data.whoLeave_photo[base64String]}">×</span><img src="${data.whoLeave_photo[base64String]}" alt="" />`
        whoPhotos.appendChild(newImgEle)
      })
    })
    .catch(error => {
      console.dir(error)
    })
}

// 事件委托：点击“审批”进入具体请假表审批页面
let userItems = document.querySelector('.user_items')
userItems.addEventListener('click', e => {
  if (e.target.classList.contains('approval_btn')) {
    // 已审批则无法点击
    if (e.target.previousElementSibling.innerHTML != '未审批') {
      popupTop.innerHTML = '已审批！'
      popup.classList.remove('hide')
      return
    }
    // 获取请假申请的 id
    let id = location.href.split('=')[1]
    getData(id)
    // 跳转到请假申请表审批页面
    location.href = location.href.split('#')[0] + `#approvalRequestForm?event_id=${id}`
  }
})
