class UserProfile {
  final String email;
  final String role;
  final String firstName;
  final String lastName;
  final String phoneNumber;
  final String address;
  final String? profilePicture;
  final PatientData? patientData;
  final DoctorData? doctorData;

  UserProfile({
    required this.email,
    required this.role,
    required this.firstName,
    required this.lastName,
    required this.phoneNumber,
    required this.address,
    this.profilePicture,
    this.patientData,
    this.doctorData,
  });

  String get fullName => '$firstName $lastName'.trim();

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      email: json['email'] ?? '',
      role: json['role'] ?? '',
      firstName: json['first_name'] ?? '',
      lastName: json['last_name'] ?? '',
      phoneNumber: json['phone_number'] ?? '',
      address: json['address'] ?? '',
      profilePicture: json['profile_picture'],
      patientData: json['patient_data'] != null
          ? PatientData.fromJson(json['patient_data'])
          : null,
    );
  }
}

class PatientData {
  final String? dateOfBirth;
  final String bloodGroup;
  final String allergies;
  final String emergencyContact;

  PatientData({
    this.dateOfBirth,
    required this.bloodGroup,
    required this.allergies,
    required this.emergencyContact,
  });

  factory PatientData.fromJson(Map<String, dynamic> json) {
    return PatientData(
      dateOfBirth: json['date_of_birth'],
      bloodGroup: json['blood_group'] ?? '',
      allergies: json['allergies'] ?? '',
      emergencyContact: json['emergency_contact'] ?? '',
    );
  }
}

class DoctorData {
  final int? categoryId;
  final String categoryName;
  final String specialization;
  final String? licenseNumber;
  final String? bio;
  final bool isVerified;

  DoctorData({
    this.categoryId,
    required this.categoryName,
    required this.specialization,
    this.licenseNumber,
    this.bio,
    required this.isVerified,
  });

  factory DoctorData.fromJson(Map<String, dynamic> json) {
    return DoctorData(
      categoryId: json['category'] as int?,
      categoryName: json['category_name'] as String? ?? 'General',
      specialization: json['specialization'] as String? ?? '',
      licenseNumber: json['license_number'] as String?,
      bio: json['bio'] as String?,
      isVerified: json['is_verified'] as bool? ?? false,
    );
  }
}

