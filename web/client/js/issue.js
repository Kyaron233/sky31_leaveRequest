// 首页
let activityListPage = document.querySelector('.form_list')
// 发布页
let issueNewActivityPage = document.querySelector('.issue_activity_page')
// 请假名单页
let userRequestFormPage = document.querySelector('.user_request_list')
// 修改活动页
let modifyActivityPage = document.querySelector('.modify_activity')
// 审批页
let approvalRequestFormPage = document.querySelector('.approval_request_form')
// 弹窗
let popup = document.querySelector('.popup_shadow')
let popupTop = popup.querySelector('.top')

// 部门名称
let departmentNames = document.querySelectorAll('h1')
departmentNames.forEach(departmentName => {
  departmentName.innerHTML = localStorage.getItem('departmentName')
})
// 创建对象存入所有可切换页面
let allPages = {
  activityList: activityListPage,
  issueNewActivity: issueNewActivityPage,
  userRequestForm: userRequestFormPage,
  modifyActivity: issueNewActivityPage,
  approvalRequestForm: approvalRequestFormPage
}
// 定义函数展示要展示的页面
function showPage(page) {
  Object.keys(allPages).forEach(key => {
    allPages[key].classList.add('hide')
  })
  page.classList.remove('hide')
}

// 在页面刷新时根据URL展示当前页面
let pageUrl = location.href.split('#')[1]?.split('?')[0] || 'activityList'
if (pageUrl === 'activityList') {
  // 获取数据渲染首页列表
  axios({
    method: 'get',
    url: '/publish'
  })
    .then(result => {
      let activityDatas = result.data
      let activityItems = document.querySelector('.activity_items')
      activityDatas?.forEach(activityData => {
        let date = new Date(activityData.event_date)
        // 转换时间格式
        const formattedDate = date.toISOString().split('T')[0].split('-').join('.')

        let item = document.createElement('li')
        item.classList.add('item')
        item.id = activityData.event_id
        item.innerHTML = `<div class="activity_name">${activityData.event_name}</div>
          <div class="expiration_date"><span class="date">${formattedDate}</span><span>（截止时间）</span></div>
        `

        activityItems.appendChild(item)
      })
      // 若有内容则隐藏背景图
      if (activityItems.querySelectorAll('.item').length != 0) {
        document.querySelector('.form_list section').style.backgroundImage = 'none'
      }
    })
    .catch(error => {
      console.dir(error)
    })
  //     `<li class="item">
  //   <div class="activity_name">活动名称活动名称活动名称活动名称活动名称活动名称</div>
  //   <div class="expiration_date"><span class="date">2025.01.23</span><span>（截止时间）</span></div>
  // </li>`
} else if (pageUrl === 'userRequestForm') {
}
showPage(allPages[pageUrl])

// 点击进入发布新活动页面
let issueActivity = document.querySelector('.issue_activity')
issueActivity.addEventListener('click', () => {
  // 修改 URL
  location.href = location.href.split('#')[0] + '#issueNewActivity'
  // 页面切换
  // showPage(issueNewActivityPage)
})

// 点击进入活动请假名单页面
let activityDataEle = document.querySelector('.header .active_content .left')
let activityName = activityDataEle.querySelector('.activity_name')
let expirationDate = activityDataEle.querySelector('.expiration_date')
let activityType = activityDataEle.querySelector('.activity_type')
let proveStatus = activityDataEle.querySelector('.prove_status')

document.addEventListener('click', e => {
  activity = e.target.closest('li.item')
  if (!activity) return
  let eventID = activity.id

  if (activity) {
    // 若点击的是已结束的活动，弹框提示“无法点击”
    if (activity.classList.contains('ended')) {
      popupTop.innerHTML = '无法点击！'
      popup.classList.remove('hide')
    }
    // 若点击的是进行中的活动，跳转到请假名单页面
    else {
      // 页面切换
      // showPage(userRequestFormPage)
      // 发送请求，获取数据并渲染到页面

      // 渲染活动信息

      // let eventID = location.href.split('=')[1]
      axios({
        url: '/main',
        params: {
          event_id: eventID
        }
      })
        .then(result => {
          console.log(result)
          let data = result.data
          // 转换时间格式
          let date = new Date(data.event_date)
          // 转换时间格式
          const formattedDate = date.toISOString().split('T')[0].split('-').join('.')

          activityName.innerHTML = data.event_name
          activityType.innerHTML = data.event_type
          proveStatus.innerHTML = data.is_photo_needed == 1 ? '是' : '否'
          expirationDate.innerHTML = formattedDate
        })
        .catch(error => {
          console.dir(error)
        })

      // 渲染成员信息
      let departmentID = localStorage.getItem('department')
      axios({
        url: '/query/history/department',
        params: {
          department_id: departmentID,
          event_id: eventID
        }
      })
        .then(result => {
          console.log(result)
          let memberMessages = result.data

          // 渲染成员列表
          let memberItems = document.querySelector('.user_items')
          // 先清空成员列表
          memberItems.innerHTML = `
            <li class="lheader"><span>正主席 / 团支书</span></li>
            <li class="lheader"><span>分管主席</span></li>
            <li class="lheader"><span>正部</span></li>
            <li class="lheader"><span>副部</span></li>
            <li class="lheader"><span>干事</span></li>
            `
          let lheads = memberItems.querySelectorAll('.lheader')
          // 用以判断各个lhead后有没有lbody，没有的隐藏
          let isDisplays = [0, 0, 0, 0, 0]
          memberMessages.forEach(memberMessage => {
            if (memberMessage.whoLeave_name.length === 2) {
              memberMessage.whoLeave_name = memberMessage.whoLeave_name.split('').join('&nbsp;&nbsp;')
            }
            let approved = '未审批'
            if (memberMessage.is_permitted === 1) {
              approved = '同意'
            } else if (memberMessage.is_permitted === -1) {
              approved = '不同意'
            }
            let li = document.createElement('li')
            li.classList.add('lbody')
            li.innerHTML = `
                <div class="name">${memberMessage.whoLeave_name}</div>
                <div class="approval_status">${approved}</div>
                <button class="approval_btn">审批</button>
              `
            let rid = memberMessage.whoLeave_role
            console.log(rid)
            if (rid === 4) {
              memberItems.insertBefore(li, lheads[1])
            } else if (rid === 3) {
              memberItems.insertBefore(li, lheads[2])
            } else if (rid === 2) {
              memberItems.insertBefore(li, lheads[3])
            } else if (rid === 1) {
              memberItems.insertBefore(li, lheads[4])
            } else {
              memberItems.appendChild(li)
            }
            let id = Math.abs(rid - 4)
            isDisplays[id] = 1
          })
          for (let i = 0; i < isDisplays.length; i++) {
            isDisplays[i] || lheads[i].classList.add('hide')
          }

          // console.log(memberItems)
          // 将请假成员信息存入内存，在页面刷新时获取并展示
          localStorage.setItem('memberItems', memberItems.outerHTML)
        })
        .catch(error => {
          console.dir(error)
        })
      // 修改 URL
      location.href = location.href.split('#')[0] + `#userRequestForm?event_id=${eventID}`
    }
  }
})

// 绑定返回事件
let backBtns = document.querySelectorAll('.back')
backBtns.forEach(backBtn =>
  backBtn.addEventListener('click', () => {
    history.back()
  })
)

// 监听到页面url发生变化时
window.addEventListener('popstate', () => {
  // 确保展示到正确的页面上
  // 若“#”后为空则返回首页
  pageUrl = location.href.split('#')[1]?.split('?')[0] || 'activityList'
  showPage(allPages[pageUrl])

  // 展示到对应页面时执行相应操作
})

// 点击“确认”移除提示框
popup.querySelector('.bottom').addEventListener('click', e => {
  if (e.target.classList.contains('close')) {
    popup.classList.add('hide')
    if (popupTop.innerHTML === '确认删除！') {
      axios({
        method: 'delete',
        url: `publish/${location.href.split('=')[1]}`
      })
        .then(result => {
          console.log(result)
          history.back()
        })
        .catch(error => {
          console.dir(error)
          history.back()
        })
    } else if (popupTop.innerHTML === '审批成功！') {
      history.back(2)
    }
  }
})
