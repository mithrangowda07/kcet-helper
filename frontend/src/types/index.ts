export interface Student {
  student_user_id: string
  type_of_student: 'counselling' | 'studying'
  email_id: string
  phone_number: string
  kcet_rank?: number
  college_code?: string
  unique_key?: string
  year_of_starting?: number
  profile_completed: boolean
}

export interface College {
  college_id: string
  college_code: string
  college_name: string
  location: string
}

export interface Branch {
  unique_key: string
  college: College
  cluster: {
    cluster_code: string
    cluster_name: string
  }
  branch_id: string
  branch_name: string
}

export interface Recommendation {
  unique_key: string
  college: College
  branch: {
    branch_id: string
    branch_name: string
  }
  cluster: {
    cluster_code: string
    cluster_name: string
  }
  category: string
  opening_rank: number
  closing_rank: number
  distance_from_rank: number
  eligibility_flag: boolean
}

export interface CounsellingChoice {
  choice_id: number
  order_of_list: number
  unique_key: string
  unique_key_data: Branch
  created_at: string
}

export interface Review {
  review_id: number
  student_user_id: string
  unique_key: string
  teaching_rating: number
  courses_rating: number
  library_rating: number
  research_rating: number
  internship_rating: number
  infrastructure_rating: number
  administration_rating: number
  extracurricular_rating: number
  safety_rating: number
  placement_rating: number
  preferred_day?: string
  preferred_time?: string
}

export interface Meeting {
  meeting_id: number
  counselling_user_id: string
  studying_user_id: string
  scheduled_time?: string
  duration_minutes: number
  meet_link?: string
  status: 'requested' | 'accepted' | 'rejected' | 'completed' | 'cancelled'
  feedback?: string
}

