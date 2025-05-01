// 立即执行函数
;(() => {
  // 事件委托：绑定“按姓名分类”和“按部门分类”按钮的点击事件
  let btns = document.querySelector('.department_details header .bottom')
  let nameContent = document.querySelector('.classified_by_name')
  let departmentContent = document.querySelector('.classified_by_department')
  btns.addEventListener('click', e => {
    // 若点击已显示列表，退出程序
    if (e.target.classList.contains('active')) return
    // 切换高亮按钮
    btns.querySelector('.active').classList.remove('active')
    e.target.classList.add('active')
    // 切换显示列表
    if (e.target.classList.contains('classified_by_name_btn')) {
      nameContent.classList.remove('hide')
      departmentContent.classList.add('hide')
    } else {
      nameContent.classList.add('hide')
      departmentContent.classList.remove('hide')
    }
  })

  // 事件委托：点击“按姓名排序”内部姓名时进入到用户请假详情页
  document.querySelector('.classified_by_name .user_items').addEventListener('click', e => {
    if (e.target.closest('.lbody')) {
      let userId = e.target.id
      getUserDetails(userId)
      location.href = location.href.split('#')[0] + `#userDetails?userId=${userId}`
    }
  })

  // 事件委托：点击“按部门排序”内部部门名称时进入到活动请假详情页
  document.querySelector('.classified_by_department .activity_items').addEventListener('click', e => {
    console.log(e.target)
    if (e.target.closest('li')) {
      let ele = e.target.closest('li')
      let event_id = ele.id
      getActivityDetails(event_id)
      // 活动名称和活动类型
      document.querySelector('.activity_details .top h1').innerHTML = ele.querySelector('.activity_name').innerHTML
      document.querySelector('.activity_details .top h2').innerHTML = ele.querySelector('span').innerHTML
      location.href = location.href.split('#')[0] + `#activityDetails?activityId=${event_id}`
    }
  })
})()
